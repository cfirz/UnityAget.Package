# Unity AI Suggestions Proxy - Deployment Guide

## Overview
This is a minimal AWS Lambda proxy that forwards requests from the Unity Editor to OpenAI's API. It performs basic Authorization header validation and relays streaming responses.

## ⚠️ Important: Timeout Limitations

**API Gateway has a hard limit of 29 seconds** for request timeouts. For GPT-5 requests that can take 60-120+ seconds, you **must use Lambda Function URLs** instead of API Gateway.

**See [MIGRATION_TO_FUNCTION_URLS.md](./MIGRATION_TO_FUNCTION_URLS.md) for migration guide.**

## Prerequisites
- AWS Account
- AWS CLI installed and configured
- AWS SAM CLI installed (for easy deployment)

## Deployment Options

### Option 1: Using AWS SAM with Function URLs (Recommended for GPT-5)

1. Install AWS SAM CLI: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html

2. Build the Lambda package:
```bash
cd proxy
sam build
```

3. Deploy:
```bash
sam deploy --guided
```

4. The deployment will output the **Lambda Function URL**. Copy this URL and use it in the Unity Editor settings.
   - Function URLs support up to **15 minutes** timeout (vs API Gateway's 29 seconds)
   - Use the URL directly or append `/suggest` (both work)

### Option 2: Manual Lambda Deployment

#### Step 1: Create Lambda Function

1. **Navigate to AWS Lambda Console:**
   - Go to https://console.aws.amazon.com/lambda/
   - Or from AWS Console home, click "Services" (top left), search for "Lambda", and click "Lambda"

2. **Create Function:**
   - Click the orange "Create function" button (top right)
   - Choose "Author from scratch"
   - **Function name:** Enter `unity-ai-suggestions-proxy` (or your preferred name)
   - **Runtime:** Select `Python 3.11`
   - **Architecture:** Leave as `x86_64`
   - Click "Create function" button (bottom right)

3. **Upload Function Code:**
   - In the function page, scroll to the "Code" tab (default view)
   - Click "Upload from" dropdown → select ".zip file"
   - Create a ZIP file containing `lambda_function.py`
   - Click "Upload" and select your ZIP file
   - Click "Save" button (top right)

4. **Configure Handler:**
   - In the "Runtime settings" section (top right of Code tab)
   - Click "Edit" button
   - **Handler:** `lambda_function.lambda_handler`
   - Click "Save"

#### Step 2: Create API Gateway

1. **Navigate to API Gateway Console:**
   - Go to https://console.aws.amazon.com/apigateway/
   - Or from AWS Console home, click "Services", search for "API Gateway", and click "API Gateway"

2. **Create REST API:**
   - Click "Create API" button
   - Under "REST API", click "Build" button
   - **API name:** Enter `unity-ai-suggestions-api` (or your preferred name)
   - **Endpoint Type:** Select "Regional"
   - Click "Create API" button (bottom right)

3. **Create Resource:**
   - In the left sidebar, click "Actions" dropdown → "Create Resource"
   - **Resource Name:** `suggest`
   - **Resource Path:** `/suggest` (auto-filled)
   - Check "Enable API Gateway CORS"
   - Click "Create Resource" button

4. **Create Method:**
   - With `/suggest` resource selected, click "Actions" dropdown → "Create Method"
   - Select "POST" from the dropdown → click the checkmark
   - **Integration type:** Select "Lambda Function"
   - **Use Lambda Proxy integration:** Check this box ✓
   - **Lambda Region:** Select your Lambda function's region
   - **Lambda Function:** Type `unity-ai-suggestions-proxy` (or your function name)
   - Click "Save" button
   - Click "OK" when prompted about Lambda permissions

5. **Enable CORS:**
   - With `/suggest` resource selected, click "Actions" dropdown → "Enable CORS"
   - Leave defaults or configure:
     - **Access-Control-Allow-Origin:** `*` (or specific domain)
     - **Access-Control-Allow-Headers:** `Authorization,Content-Type,X-API-Key` (include X-API-Key as fallback)
     - **Access-Control-Allow-Methods:** `POST,OPTIONS`
   - Click "Enable CORS and replace existing CORS headers"

#### Step 3: Deploy API Gateway

1. **Deploy API:**
   - Click "Actions" dropdown → "Deploy API"
   - **Deployment stage:** Select "[New Stage]" or choose existing
   - **Stage name:** `prod` (or `dev`)
   - **Stage description:** Optional
   - Click "Deploy" button

2. **Get Endpoint URL:**
   - After deployment, you'll see the "Invoke URL" at the top
   - Copy this URL and append `/suggest` (e.g., `https://abc123.execute-api.us-east-1.amazonaws.com/prod/suggest`)
   - Use this full URL in Unity Editor settings

### Option 3: Using AWS Function URL (Recommended for Long-Running Requests)

#### Step 1: Create Lambda Function

1. **Navigate to AWS Lambda Console:**
   - Go to https://console.aws.amazon.com/lambda/
   - Or from AWS Console home, click "Services" (top left), search for "Lambda", and click "Lambda"

2. **Create Function:**
   - Click the orange "Create function" button (top right)
   - Choose "Author from scratch"
   - **Function name:** Enter `unity-ai-suggestions-proxy` (or your preferred name)
   - **Runtime:** Select `Python 3.11`
   - **Architecture:** Leave as `x86_64`
   - Click "Create function" button (bottom right)

3. **Upload Function Code:**
   - In the function page, scroll to the "Code" tab (default view)
   - Click "Upload from" dropdown → select ".zip file"
   - Create a ZIP file containing `lambda_function.py`
   - Click "Upload" and select your ZIP file
   - Click "Save" button (top right)

4. **Configure Handler:**
   - In the "Runtime settings" section (top right of Code tab)
   - Click "Edit" button
   - **Handler:** `lambda_function.lambda_handler`
   - Click "Save"

#### Step 2: Enable Function URL

1. **Navigate to Function URL Settings:**
   - In your Lambda function page, click the "Configuration" tab (top menu)
   - In the left sidebar under "Configuration", click "Function URL"
   - Click "Create function URL" button

2. **Configure Function URL:**
   - **Auth type:** Select `NONE` (or `AWS_IAM` for additional security)
   - **CORS:** Click "Configure cross-origin resource sharing (CORS)"
     - **Access-Control-Allow-Origin:** Enter `*` (or specific domain)
     - **Access-Control-Allow-Headers:** Enter `Authorization,Content-Type`
     - **Access-Control-Allow-Methods:** Enter `POST,OPTIONS`
     - Click "Save" button
   - **Invoke mode:** Select `RESPONSE_STREAM` (for true streaming support)
   - Click "Save" button (bottom right)

3. **Copy Function URL:**
   - After creation, you'll see the Function URL displayed (e.g., `https://abc123.lambda-url.us-east-1.on.aws/`)
   - Copy this URL - use it directly in Unity Editor settings
   - No need to append any paths - use the URL as-is

**Note:** For true streaming support, use Lambda Function URLs with RESPONSE_STREAM mode. API Gateway will buffer the entire response before sending it to the client.

## Configuration

The proxy requires no configuration - it's a pure pass-through. Just deploy and use the endpoint URL in Unity Editor settings.

## Cost

AWS Lambda free tier includes:
- 1M requests/month
- 400,000 GB-seconds compute time/month

For typical usage, this should be well within the free tier.

## Security Notes

- The proxy performs minimal validation (Authorization header format check)
- API keys are passed through but never logged or stored
- Consider adding AWS_IAM authentication on Function URL for additional security
- The proxy adds CORS headers to allow Unity Editor to call it

## Troubleshooting

### Error: "invalid key=value pair (missing equal-sign) in Authorization header"

This error typically occurs when API Gateway has **AWS_IAM authorization** enabled on the method. The proxy expects **no authorization** (or NONE) so it can handle custom Bearer tokens.

**Fix Option 1 (Recommended):**
1. Go to API Gateway Console → Your API → `/suggest` resource → POST method
2. Click on "Method Request"
3. Under "Authorization", ensure it's set to **"NONE"** (not "AWS_IAM")
4. Click "Save"
5. Redeploy the API (Actions → Deploy API)

**Fix Option 2 (Workaround):**
If you can't change the authorization settings, the proxy now supports a fallback header:
- The Unity client will automatically send both `Authorization` and `X-API-Key` headers
- If API Gateway blocks `Authorization`, Lambda will use `X-API-Key` instead
- Make sure CORS allows `X-API-Key` header (see CORS configuration above)
- Redeploy your Lambda function with the updated code

### Error: "Missing Authorization header"

If you see this error with debug info showing header keys, it means API Gateway is not passing the Authorization header to Lambda. Check:
- CORS configuration allows `Authorization` header
- Method uses "Lambda Proxy Integration"
- No API Gateway authorizers are configured

## Testing

Test the proxy with curl:
```bash
curl -X POST https://YOUR_API_URL/suggest \
  -H "Authorization: Bearer sk-YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4",
    "messages": [{"role": "user", "content": "Hello"}],
    "stream": true,
    "temperature": 0.7,
    "max_output_tokens": 100
  }'
```

## Files

- `lambda_function.py` - Python Lambda function
- `template.yaml` - AWS SAM template for deployment
- `requirements.txt` - Empty (uses standard library only)

