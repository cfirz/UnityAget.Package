# AWS Lambda Testing Guide

This guide explains how to test your Lambda function directly on AWS using the AWS Console test feature.

## Prerequisites

1. Your Lambda function is deployed to AWS
2. You have access to the AWS Console
3. You have a valid OpenAI API key (starts with `sk-`)

## Step-by-Step Instructions

### 1. Open AWS Lambda Console

1. Go to [AWS Lambda Console](https://console.aws.amazon.com/lambda/)
2. Navigate to your function (likely named something like `unity-ai-proxy` or similar)
3. Click on your function name to open it

### 2. Create a Test Event

1. Click on the **"Test"** tab (or find the **"Test"** button in the top right)
2. If this is your first test, you'll see a prompt to create a test event
3. Click **"Create new test event"** or **"Configure test event"**
4. Select **"Create new test event"**
5. Give it a name: `agent-mode-test` or `chat-mode-test`

### 3. Use the Test Event JSON

#### For Agent Mode (Non-Streaming) Test:

Copy the contents of `test_event_agent_mode.json` and paste it into the test event editor.

**IMPORTANT:** Replace `sk-your-openai-api-key-here` with your actual OpenAI API key!

```json
{
  "httpMethod": "POST",
  "path": "/suggest",
  "headers": {
    "Authorization": "Bearer sk-YOUR-ACTUAL-API-KEY-HERE",
    "Content-Type": "application/json"
  },
  "body": "{\"model\":\"gpt-4o-mini\",\"messages\":[{\"role\":\"system\",\"content\":\"You are a helpful assistant.\"},{\"role\":\"user\",\"content\":\"Say hello in one sentence.\"}],\"stream\":false,\"temperature\":0.7,\"max_tokens\":2000,\"max_output_tokens\":2000}",
  "isBase64Encoded": false
}
```

#### For Chat Mode (Streaming) Test:

Copy the contents of `test_event_chat_mode.json` and paste it into the test event editor.

**IMPORTANT:** Replace `sk-your-openai-api-key-here` with your actual OpenAI API key!

```json
{
  "httpMethod": "POST",
  "path": "/suggest",
  "headers": {
    "Authorization": "Bearer sk-YOUR-ACTUAL-API-KEY-HERE",
    "Content-Type": "application/json"
  },
  "body": "{\"model\":\"gpt-4o-mini\",\"messages\":[{\"role\":\"system\",\"content\":\"You are a helpful assistant.\"},{\"role\":\"user\",\"content\":\"Say hello in one sentence.\"}],\"stream\":true,\"temperature\":0.7,\"max_tokens\":2000,\"max_output_tokens\":2000}",
  "isBase64Encoded": false
}
```

### 4. Save and Run the Test

1. Click **"Save"** to save the test event
2. Click **"Test"** to run the test
3. Wait for the execution to complete (should take a few seconds)

### 5. Review the Results

After the test completes, you'll see:

#### Execution Results Section:
- **Execution result**: Shows if the test succeeded or failed
- **Function Logs**: Shows the CloudWatch logs (check for `[Lambda]` prefixed messages)
- **Response**: Shows the actual response returned by the Lambda function

#### What to Look For:

**For Agent Mode (stream: false):**
- ✅ **Success**: `statusCode: 200` with `Content-Type: application/json`
- ✅ **Body**: Should contain a complete JSON response with `choices[0].message.content`
- ❌ **Error**: Check for error messages in the response body or logs

**For Chat Mode (stream: true):**
- ✅ **Success**: `statusCode: 200` with `Content-Type: text/event-stream`
- ✅ **Body**: Should contain SSE formatted data (`data: {...}`)
- ❌ **Error**: Check for error messages in the response body or logs

### 6. Check CloudWatch Logs

1. Click on the **"Monitor"** tab in your Lambda function
2. Click **"View CloudWatch logs"** or go to CloudWatch directly
3. Look for log entries with `[Lambda]` prefix to see detailed debugging info

### Common Issues to Check

1. **401 Unauthorized**: API key is missing or invalid
   - Solution: Make sure your API key starts with `sk-` and is valid

2. **400 Bad Request**: Invalid JSON in body
   - Solution: Check that the JSON in the `body` field is properly escaped

3. **502 Bad Gateway**: Error connecting to OpenAI
   - Solution: Check your network/VPC configuration and OpenAI API status

4. **500 Internal Server Error**: Lambda function error
   - Solution: Check CloudWatch logs for Python traceback

### Comparing Agent vs Chat Mode

Run both tests and compare:

1. **Response Content-Type**:
   - Agent mode should return: `application/json`
   - Chat mode should return: `text/event-stream`

2. **Response Body Format**:
   - Agent mode: Complete JSON object with `choices[0].message.content`
   - Chat mode: SSE format with `data: {...}` lines

3. **Response Size**:
   - Agent mode: Single complete response
   - Chat mode: Multiple SSE chunks

## Troubleshooting

If agent mode returns an error but chat mode works:

1. Check the `stream` field in the request body - it should be `false` for agent mode
2. Check CloudWatch logs for the `[Lambda]` debug messages
3. Verify the response Content-Type is `application/json` (not `text/event-stream`)
4. Check if the response body is valid JSON (not SSE format)

If you see errors related to JSON parsing in the Lambda logs, that's likely the issue - the Lambda might be receiving or returning SSE format when it should be returning JSON.

