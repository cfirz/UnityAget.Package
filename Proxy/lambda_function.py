"""
AWS Lambda function for Unity AI Suggestions proxy.
Routes requests to OpenAI (Responses API) or Anthropic (Messages API) and performs light request-shaping:
- Extracts system instructions for OpenAI Responses
- Translates token limit fields (max_output_tokens vs max_tokens)
- Buffers streaming responses for API Gateway compatibility
"""

import json
import os
import re
from typing import Dict, Any, Tuple, List, Optional
import urllib.request
import urllib.parse

def _extract_system_instructions_and_non_system_messages(request_data: Dict[str, Any]) -> Tuple[Optional[str], List[Dict[str, Any]]]:
    """
    For OpenAI Responses API:
    - system instructions should be top-level 'instructions'
    - non-system messages become 'input' items

    We support both:
    - request_data['system'] (preferred from Unity client)
    - any messages with role == 'system' (backward compatibility)
    """
    instructions_parts = []

    system_field = request_data.get('system')
    if isinstance(system_field, str) and system_field.strip():
        instructions_parts.append(system_field.strip())

    non_system: List[Dict[str, Any]] = []
    for msg in request_data.get('messages', []) or []:
        role = (msg.get('role') or '').strip().lower()
        content = msg.get('content', '')
        if role == 'system':
            if isinstance(content, str) and content.strip():
                instructions_parts.append(content.strip())
            continue
        non_system.append(msg)

    instructions = "\n\n".join([p for p in instructions_parts if p])
    return (instructions if instructions else None), non_system

def _openai_messages_to_responses_input(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convert chat-completions style messages into Responses API 'input' items.
    This uses the canonical content-part format for compatibility.
    """
    items: List[Dict[str, Any]] = []
    for msg in messages or []:
        role = (msg.get('role') or '').strip().lower() or 'user'
        content = msg.get('content', '')
        if content is None:
            content = ""
        if not isinstance(content, str):
            content = str(content)

        # Use content parts; keep roles to preserve conversation shape.
        # For Responses API, 'input' should use input_* parts even for assistant history items.
        part_type = 'input_text'

        items.append({
            'role': role,
            'content': [
                {'type': part_type, 'text': content}
            ]
        })
    return items

def _safe_len(x: Any) -> int:
    try:
        return len(x)
    except Exception:
        return 0

def _log_request_summary(provider_name: str, api_request: Dict[str, Any], is_streaming_request: bool) -> None:
    model = api_request.get('model', '')
    if provider_name == 'Claude':
        msg_count = _safe_len(api_request.get('messages', []))
        print(f"[Lambda] Request to Claude - stream: {is_streaming_request}, model: {model}, messages: {msg_count}")
        return

    # OpenAI Responses: log using 'input' (not 'messages').
    input_items = api_request.get('input', [])
    input_count = _safe_len(input_items) if isinstance(input_items, list) else 0
    print(f"[Lambda] Request to OpenAI - stream: {is_streaming_request}, model: {model}, input_items: {input_count}")

def _log_user_message_sizes(provider_name: str, api_request: Dict[str, Any]) -> None:
    """
    Best-effort logging of user message text sizes without assuming a specific schema.
    """
    if provider_name == 'Claude':
        for i, msg in enumerate(api_request.get('messages', []) or []):
            if msg.get('role') == 'user':
                content_length = len(msg.get('content', '') or '')
                print(f"[Lambda] User message {i+1} content length: {content_length} chars")
        return

    # OpenAI Responses: iterate 'input' items and sum text lengths from content parts.
    input_items = api_request.get('input', []) or []
    if not isinstance(input_items, list):
        return

    user_idx = 0
    for item in input_items:
        if not isinstance(item, dict):
            continue
        if (item.get('role') or '').strip().lower() != 'user':
            continue

        user_idx += 1
        parts = item.get('content', [])
        total = 0
        if isinstance(parts, list):
            for part in parts:
                if isinstance(part, dict):
                    total += len(part.get('text', '') or '')
        else:
            total = len(str(parts))
        print(f"[Lambda] User input item {user_idx} content length: {total} chars")

def normalize_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize event format to support both API Gateway and Lambda Function URLs.
    Function URLs use a different event structure than API Gateway.
    """
    # Check if this is a Function URL event (has requestContext.http)
    if 'requestContext' in event and 'http' in event.get('requestContext', {}):
        # Lambda Function URL event format
        http_context = event['requestContext']['http']
        normalized = {
            'httpMethod': http_context.get('method', 'POST'),
            'path': http_context.get('path', '/'),
            'headers': event.get('headers', {}) or {},
            'body': event.get('body', '{}'),
            'isBase64Encoded': event.get('isBase64Encoded', False)
        }
        return normalized
    else:
        # API Gateway event format (already normalized)
        return event

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for /suggest endpoint.
    Supports both API Gateway and Lambda Function URL event formats.
    Expects POST request with:
    - Headers: Authorization: Bearer {apiKey} or x-api-key: {apiKey}
    - Body: { model, messages, stream, temperature, max_output_tokens, provider }
    """
    # Initialize variables for error handling
    provider = 'OpenAI'
    timeout_seconds = 90
    
    # Normalize event to support both API Gateway and Function URLs
    event = normalize_event(event)
    
    # Log request details for debugging
    print(f"[Lambda] Handler invoked. Event keys: {list(event.keys())}")
    print(f"[Lambda] Event type: {type(event)}")
    print(f"[Lambda] HTTP Method: {event.get('httpMethod', 'N/A')}")
    print(f"[Lambda] Path: {event.get('path', 'N/A')}")
    print(f"[Lambda] Headers: {list(event.get('headers', {}).keys())}")
    
    try:
        # Extract Authorization header or fallback to X-API-Key custom header
        # API Gateway may block Authorization header if AWS_IAM auth is enabled
        headers = event.get('headers', {}) or {}
        
        # Try Authorization header first
        auth_header = headers.get('Authorization') or headers.get('authorization', '')
        
        # Fallback to custom header if Authorization is blocked by API Gateway
        api_key = None
        if auth_header:
            if auth_header.startswith('Bearer '):
                api_key = auth_header.replace('Bearer ', '').strip()
            else:
                # If Authorization header exists but doesn't start with Bearer, it might be malformed
                # Try to extract anyway, or check if it's already just the key
                api_key = auth_header.strip()
        
        # Fallback to X-API-Key header
        if not api_key:
            api_key = (
                headers.get('X-API-Key') or 
                headers.get('x-api-key') or 
                headers.get('X-Api-Key') or
                ''
            ).strip()
        
        if not api_key:
            return {
                'statusCode': 401,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Missing API key. Provide either Authorization: Bearer {key} or X-API-Key header',
                    'debug': {
                        'headers_available': list(headers.keys()),
                        'auth_header_present': bool(auth_header)
                    }
                })
            }
        
        # Parse request body
        # Handle base64 encoded body (API Gateway sometimes sends this)
        body = event.get('body', '{}')
        if isinstance(body, str):
            # Check if body is base64 encoded
            if event.get('isBase64Encoded', False):
                import base64
                body = base64.b64decode(body).decode('utf-8')
            try:
                request_data = json.loads(body)
            except json.JSONDecodeError as e:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'error': f'Invalid JSON in request body: {str(e)}',
                        'body_preview': body[:200] if len(body) > 200 else body
                    })
                }
        else:
            request_data = body
        
        # Validate required fields
        if not isinstance(request_data.get('messages'), list) or len(request_data.get('messages', [])) == 0:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Missing or empty messages array in request body'})
            }
        
        # Determine provider from X-Provider header or request body
        provider_header = (
            headers.get('X-Provider') or 
            headers.get('x-provider') or 
            headers.get('X-Provider-Name') or
            ''
        ).strip()
        
        # Check request body for provider field
        provider_from_body = request_data.get('provider', '').strip() if isinstance(request_data.get('provider'), str) else None
        
        # Determine provider (default to OpenAI for backward compatibility)
        provider = 'OpenAI'
        if provider_header:
            provider = provider_header
        elif provider_from_body:
            provider = provider_from_body
        
        # Normalize provider name (case-insensitive)
        provider_lower = provider.lower()
        if provider_lower == 'claude' or provider_lower == 'anthropic':
            provider = 'Claude'
        else:
            provider = 'OpenAI'
        
        # Validate API key format based on provider
        if provider == 'OpenAI':
            if not api_key.startswith('sk-'):
                return {
                    'statusCode': 401,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({'error': 'Invalid API key format. OpenAI keys start with "sk-"'})
                }
        elif provider == 'Claude':
            if not api_key.startswith('sk-ant-'):
                return {
                    'statusCode': 401,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({'error': 'Invalid API key format. Claude keys start with "sk-ant-"'})
                }
        
        # Determine API URL and endpoint based on provider
        if provider == 'Claude':
            api_url = 'https://api.anthropic.com/v1/messages'
        else:
            # OpenAI: migrate to Responses API
            api_url = 'https://api.openai.com/v1/responses'
        
        # Prepare request based on provider
        is_streaming_request = request_data.get('stream', True)
        model_name = request_data.get('model', 'gpt-4' if provider == 'OpenAI' else 'claude-sonnet-4-20250514')
        
        if provider == 'Claude':
            # Claude API format
            claude_request = {
                'model': model_name,
                'messages': request_data.get('messages', []),
                'max_tokens': (
                    request_data.get('max_tokens') or 
                    request_data.get('max_output_tokens') or 
                    4096
                )
            }
            
            # Claude requires system prompt as top-level parameter (not in messages array)
            # The C# client extracts system messages and sends them as 'system' field
            if 'system' in request_data and request_data.get('system'):
                claude_request['system'] = request_data.get('system')
            
            # Claude supports temperature
            if 'temperature' in request_data:
                claude_request['temperature'] = request_data.get('temperature', 0.7)
            
            # Claude supports streaming
            if is_streaming_request:
                claude_request['stream'] = True
            
            api_request = claude_request
            req_data_json = json.dumps(api_request)
            req_data = req_data_json.encode('utf-8')
            
            # Claude uses x-api-key header and anthropic-version header
            request_headers = {
                'x-api-key': api_key,
                'anthropic-version': '2023-06-01',
                'Content-Type': 'application/json',
                'User-Agent': 'Unity-AI-Assistant/1.0 (AWS Lambda)'
            }
            
            _log_request_summary(provider, api_request, is_streaming_request)
        else:
            # OpenAI Responses API format
            instructions, non_system_messages = _extract_system_instructions_and_non_system_messages(request_data)

            openai_request = {
                'model': model_name,
                'input': _openai_messages_to_responses_input(non_system_messages),
                'stream': is_streaming_request
            }

            if instructions:
                openai_request['instructions'] = instructions

            # Temperature is best-effort. Unity omits it when unsupported.
            if request_data.get('temperature') is not None:
                openai_request['temperature'] = request_data.get('temperature')

            # Use max_output_tokens for Responses API (fallback to other fields for backward compatibility).
            max_output_tokens = (
                request_data.get('max_output_tokens') or
                request_data.get('max_completion_tokens') or
                request_data.get('max_tokens') or
                2000
            )
            openai_request['max_output_tokens'] = max_output_tokens

            # Structured output (agent mode): pass through if present.
            if isinstance(request_data.get('response_format'), dict):
                openai_request['response_format'] = request_data.get('response_format')

            # Optional reasoning controls (best-effort).
            reasoning_effort = request_data.get('reasoning_effort')
            if isinstance(reasoning_effort, str) and reasoning_effort.strip():
                openai_request['reasoning'] = {'effort': reasoning_effort.strip()}
            
            api_request = openai_request
            req_data_json = json.dumps(api_request)
            req_data = req_data_json.encode('utf-8')
            
            # OpenAI uses Authorization: Bearer header
            request_headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
                'User-Agent': 'Unity-AI-Assistant/1.0 (AWS Lambda)'
            }
            
            _log_request_summary(provider, api_request, is_streaming_request)
        
        # Calculate total request size for logging
        print(f"[Lambda] Request size: {len(req_data)} bytes, JSON length: {len(req_data_json)} chars")
        
        # Log user message size if present
        _log_user_message_sizes(provider, api_request)
        
        # Create HTTP request
        req = urllib.request.Request(
            api_url,
            data=req_data,
            headers=request_headers
        )
        
        # Check if streaming is enabled
        is_streaming = is_streaming_request
        
        # Stream response from API and buffer it
        # Note: API Gateway doesn't support true streaming, so we buffer the response
        # Use longer timeout for non-streaming when file content is included (large requests)
        # Check if request contains file content (rough heuristic: large user message)
        has_file_content = False
        if isinstance(request_data.get('messages'), list):
            for msg in request_data.get('messages', []):
                if msg.get('role') == 'user' and 'Current File Content' in msg.get('content', ''):
                    has_file_content = True
                    break
        
        # Use longer timeout for non-streaming requests with file content
        # APIs can take longer to process large requests
        # GPT-5 models are slower and need more time
        if is_streaming:
            timeout_seconds = 290  # Streaming requests get longer timeout
        else:
            # GPT-5 models need more time (they're slower)
            is_gpt5_model = model_name.startswith('gpt-5')
            if has_file_content:
                timeout_seconds = 180  # 3 minutes for file editing requests
                print(f"[Lambda] Detected file content in request, using extended timeout: {timeout_seconds}s")
            elif is_gpt5_model:
                timeout_seconds = 120  # 2 minutes for GPT-5 (slower model)
                print(f"[Lambda] GPT-5 model detected, using extended timeout: {timeout_seconds}s")
            else:
                timeout_seconds = 90  # 90 seconds default for other models
        print(f"[Lambda] Calling {provider} API with timeout: {timeout_seconds}s, streaming: {is_streaming}")
        print(f"[Lambda] Request URL: {api_url}")
        # Log headers but mask API key for security
        safe_headers = {}
        for k, v in req.headers.items():
            if k.lower() == 'authorization' or k.lower() == 'x-api-key':
                safe_headers[k] = v[:10] + '...' if len(v) > 10 else '...'
            else:
                safe_headers[k] = v
        print(f"[Lambda] Request headers: {safe_headers}")
        
        try:
            response = urllib.request.urlopen(req, timeout=timeout_seconds)
        except Exception as req_e:
            print(f"[Lambda] ERROR during urlopen: {type(req_e).__name__}: {str(req_e)}")
            raise
        
        with response:
            # Log response status and headers
            print(f"[Lambda] Response status: {response.status}, reason: {response.reason}")
            print(f"[Lambda] Response headers: {dict(response.headers)}")
            
            response_body = response.read().decode('utf-8')
            
            # Log response size for debugging (only for non-streaming to avoid log spam)
            if not is_streaming:
                print(f"[Lambda] Non-streaming response received: {len(response_body)} bytes")
                # Validate response is valid JSON for non-streaming
                try:
                    json.loads(response_body)
                    print("[Lambda] Response is valid JSON")
                except json.JSONDecodeError as je:
                    print(f"[Lambda] ERROR: Response is not valid JSON: {str(je)}")
                    # Return error instead of invalid response
                    return {
                        'statusCode': 502,
                        'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*'
                        },
                        'body': json.dumps({
                            'error': f'{provider} API returned invalid JSON response',
                            'error_details': str(je),
                            'response_preview': response_body[:500]
                        })
                    }
            
            # Set appropriate Content-Type based on streaming mode
            if is_streaming:
                content_type = 'text/event-stream'
                # Headers for streaming response
                response_headers = {
                    'Content-Type': content_type,
                    'Access-Control-Allow-Origin': '*',
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive'
                }
            else:
                content_type = 'application/json'
                # Headers for non-streaming response (no Connection header)
                response_headers = {
                    'Content-Type': content_type,
                    'Access-Control-Allow-Origin': '*'
                }
            
            # Return response with appropriate Content-Type
            print(f"[Lambda] Preparing response - Content-Type: {response_headers['Content-Type']}, Body length: {len(response_body)}")
            
            # Ensure response_body is a string (not bytes)
            if isinstance(response_body, bytes):
                response_body = response_body.decode('utf-8')
            elif not isinstance(response_body, str):
                response_body = str(response_body)
            
            # Validate response format for API Gateway
            # API Gateway requires headers to be strings (not bytes) and body to be a string
            # Ensure all header values are strings
            validated_headers = {}
            for key, value in response_headers.items():
                if isinstance(value, bytes):
                    validated_headers[key] = value.decode('utf-8')
                elif not isinstance(value, str):
                    validated_headers[key] = str(value)
                else:
                    validated_headers[key] = value
            
            # Ensure body is a string and doesn't contain problematic characters
            if isinstance(response_body, bytes):
                validated_body = response_body.decode('utf-8')
            elif not isinstance(response_body, str):
                validated_body = str(response_body)
            else:
                validated_body = response_body
            
            # Validate JSON format if it's supposed to be JSON
            if not is_streaming:
                try:
                    # Validate it's valid JSON by parsing it
                    json.loads(validated_body)
                    print("[Lambda] Response body is valid JSON")
                except json.JSONDecodeError as je:
                    print(f"[Lambda] WARNING: Response body is not valid JSON: {str(je)}")
                    # Don't fail here, just log - maybe API returned non-JSON for some reason
            
            result = {
                'statusCode': 200,
                'headers': validated_headers,
                'body': validated_body,
                'isBase64Encoded': False
            }
            
            # Validate all required fields are present and correct types
            if not isinstance(result['statusCode'], int):
                raise ValueError(f"statusCode must be int, got {type(result['statusCode'])}")
            if not isinstance(result['headers'], dict):
                raise ValueError(f"headers must be dict, got {type(result['headers'])}")
            if not isinstance(result['body'], str):
                raise ValueError(f"body must be str, got {type(result['body'])}")
            
            # Additional validation: ensure headers dict values are all strings
            for key, value in result['headers'].items():
                if not isinstance(value, str):
                    raise ValueError(f"Header '{key}' value must be str, got {type(value)}")
            
            print(f"[Lambda] Returning response with statusCode: {result['statusCode']}, body type: {type(result['body'])}, body length: {len(result['body'])}")
            print(f"[Lambda] Response headers: {list(result['headers'].keys())}")
            
            # Try to serialize the response to ensure it's valid for API Gateway
            try:
                json.dumps(result, default=str)
                print("[Lambda] Response serializes correctly")
            except Exception as ser_e:
                print(f"[Lambda] WARNING: Response serialization test failed: {str(ser_e)}")
                # Continue anyway - API Gateway might handle it differently
            
            # Final check: ensure body doesn't exceed API Gateway limits (10MB)
            # But more importantly, ensure it's a valid string
            if len(result['body']) > 10 * 1024 * 1024:  # 10MB
                print(f"[Lambda] WARNING: Response body is very large: {len(result['body'])} bytes")
            
            # Log first 200 chars of body for debugging
            body_preview = result['body'][:200] if len(result['body']) > 200 else result['body']
            print(f"[Lambda] Response body preview: {body_preview}")
            
            return result
    except urllib.error.HTTPError as e:
        try:
            error_body_raw = e.read().decode('utf-8')
        except:
            error_body_raw = f'HTTP {e.code}: {e.reason}'
        
        # Ensure error body is a string
        if isinstance(error_body_raw, bytes):
            error_body_raw = error_body_raw.decode('utf-8')
        elif not isinstance(error_body_raw, str):
            error_body_raw = str(error_body_raw)
        
        # Check if error body is HTML (like Cloudflare error pages)
        is_html_response = (
            error_body_raw.strip().startswith('<html') or 
            error_body_raw.strip().startswith('<!DOCTYPE') or
            '<html' in error_body_raw.lower() or
            'cloudflare' in error_body_raw.lower()
        )
        
        if is_html_response:
            # Extract meaningful error info from HTML or provide generic message
            print(f"[Lambda] Received HTML error response (likely Cloudflare): HTTP {e.code}")
            print(f"[Lambda] HTML preview: {error_body_raw[:500]}")
            
            # Try to extract error message from HTML
            error_message = f'Gateway error (HTTP {e.code})'
            if e.code == 502:
                error_message = f'Bad Gateway: Unable to reach {provider} API. This may be due to network issues, Cloudflare blocking, or API service problems.'
            elif e.code == 503:
                error_message = f'Service Unavailable: {provider} API is temporarily unavailable.'
            elif e.code == 504:
                error_message = 'Gateway Timeout: The request took too long to process.'
            
            error_body = json.dumps({
                'error': error_message,
                'http_status': e.code,
                'http_reason': e.reason,
                'details': 'Received HTML error page instead of JSON response. This usually indicates a gateway/proxy issue.',
                'html_preview': error_body_raw[:200] if len(error_body_raw) > 200 else error_body_raw
            })
        else:
            # Try to parse as JSON, otherwise return as-is
            try:
                parsed_error = json.loads(error_body_raw)
                error_body = json.dumps(parsed_error)
            except json.JSONDecodeError:
                # Not JSON, return as structured error
                error_body = json.dumps({
                    'error': f'HTTP {e.code}: {e.reason}',
                    'http_status': e.code,
                    'http_reason': e.reason,
                    'response_body': error_body_raw[:1000] if len(error_body_raw) > 1000 else error_body_raw
                })
        
        return {
            'statusCode': 502 if e.code >= 500 else e.code,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': error_body,
            'isBase64Encoded': False
        }
    except urllib.error.URLError as e:
        import traceback
        error_msg = str(e)
        # Check if it's a timeout error
        if 'timed out' in error_msg.lower() or 'timeout' in error_msg.lower():
            error_details = {
                'error': f'Request timed out after {timeout_seconds}s. The request may be too large or {provider} API is taking longer than expected.',
                'error_type': type(e).__name__,
                'suggestion': 'Try using streaming mode or reducing the request size',
                'timeout_seconds': timeout_seconds
            }
        else:
            error_details = {
                'error': f'Network error connecting to {provider} API: {error_msg}',
                'error_type': type(e).__name__,
                'traceback': traceback.format_exc()
            }
        print(f"[Lambda] URLError: {error_details}")
        
        # Ensure error body is a valid JSON string
        try:
            error_body_str = json.dumps(error_details)
        except Exception as json_err:
            print(f"[Lambda] Failed to serialize error details: {str(json_err)}")
            error_body_str = json.dumps({
                'error': f'Network error: {error_msg}',
                'error_type': type(e).__name__
            })
        
        return {
            'statusCode': 502,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': error_body_str,
            'isBase64Encoded': False
        }
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        print(f"[Lambda] EXCEPTION: {type(e).__name__}: {str(e)}")
        print(f"[Lambda] TRACEBACK:\n{error_traceback}")
        
        error_details = {
            'error': f'Proxy error: {str(e)}',
            'error_type': type(e).__name__,
            'traceback': error_traceback,
            'event_keys': list(event.keys()) if isinstance(event, dict) else 'not a dict'
        }
        
        # Ensure error body is a valid JSON string
        try:
            error_body_str = json.dumps(error_details)
        except Exception as json_err:
            print(f"[Lambda] Failed to serialize error details: {str(json_err)}")
            error_body_str = json.dumps({
                'error': f'Proxy error: {str(e)}',
                'error_type': type(e).__name__
            })
        
        error_response = {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': error_body_str,
            'isBase64Encoded': False
        }
        
        # Validate error response format
        if not isinstance(error_response['statusCode'], int):
            error_response['statusCode'] = 500
        if not isinstance(error_response['headers'], dict):
            error_response['headers'] = {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        if not isinstance(error_response['body'], str):
            error_response['body'] = json.dumps({'error': 'Unknown error occurred'})
        
        print(f"[Lambda] Returning error response: {error_response['statusCode']}")
        return error_response

