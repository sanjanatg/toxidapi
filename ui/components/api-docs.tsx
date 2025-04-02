import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"

export default function ApiDocs() {
  return (
    <div className="space-y-6">
      <div className="prose max-w-none">
        <h2>API Documentation</h2>
        <p>
          ToxidAPI provides a RESTful API for content moderation and text analysis. Below you&apos;ll find the available
          endpoints, request formats, and response examples.
        </p>
      </div>

      <Tabs defaultValue="endpoints">
        <TabsList>
          <TabsTrigger value="endpoints">Endpoints</TabsTrigger>
          <TabsTrigger value="authentication">Authentication</TabsTrigger>
          <TabsTrigger value="rate-limits">Rate Limits</TabsTrigger>
          <TabsTrigger value="errors">Error Handling</TabsTrigger>
        </TabsList>

        <TabsContent value="endpoints" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg flex items-center">
                  <Badge className="mr-2 bg-green-600">POST</Badge>
                  /api/analyze
                </CardTitle>
                <Badge variant="outline">v1</Badge>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600 mb-4">
                Analyzes text for toxicity, sentiment, and inappropriate content.
              </p>

              <div className="space-y-4">
                <div>
                  <h4 className="text-sm font-medium mb-2">Request Body</h4>
                  <pre className="bg-gray-100 p-3 rounded-md text-sm overflow-x-auto">
                    {`{
  "text": "Text to analyze",
  "options": {
    "includeToxicity": true,
    "includeSentiment": true,
    "includeFlaggedWords": true
  }
}`}
                  </pre>
                </div>

                <div>
                  <h4 className="text-sm font-medium mb-2">Response</h4>
                  <pre className="bg-gray-100 p-3 rounded-md text-sm overflow-x-auto">
                    {`{
  "text": "Text to analyze",
  "toxicity": {
    "score": 0.1234,
    "isToxic": false
  },
  "sentiment": {
    "score": 0.8765,
    "label": "POSITIVE"
  },
  "flaggedWords": {
    "count": 0,
    "severity": 0,
    "words": [],
    "categories": []
  },
  "processingTime": 0.5678
}`}
                  </pre>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg flex items-center">
                  <Badge className="mr-2 bg-green-600">POST</Badge>
                  /api/analyze/batch
                </CardTitle>
                <Badge variant="outline">v1</Badge>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600 mb-4">Analyzes multiple text inputs in a single request.</p>

              <div className="space-y-4">
                <div>
                  <h4 className="text-sm font-medium mb-2">Request Body</h4>
                  <pre className="bg-gray-100 p-3 rounded-md text-sm overflow-x-auto">
                    {`{
  "texts": [
    "First text to analyze",
    "Second text to analyze"
  ],
  "options": {
    "includeToxicity": true,
    "includeSentiment": true,
    "includeFlaggedWords": true
  }
}`}
                  </pre>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="authentication">
          <Card>
            <CardContent className="pt-6">
              <h3 className="text-lg font-medium mb-4">Authentication</h3>
              <p className="mb-4">
                ToxidAPI uses API keys for authentication. You can obtain an API key from your dashboard.
              </p>

              <div className="space-y-4">
                <div>
                  <h4 className="text-sm font-medium mb-2">API Key Authentication</h4>
                  <p className="text-sm text-gray-600 mb-2">Include your API key in the request headers:</p>
                  <pre className="bg-gray-100 p-3 rounded-md text-sm overflow-x-auto">
                    {`Authorization: Bearer YOUR_API_KEY`}
                  </pre>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="rate-limits">
          <Card>
            <CardContent className="pt-6">
              <h3 className="text-lg font-medium mb-4">Rate Limits</h3>
              <p className="mb-4">To ensure fair usage and system stability, ToxidAPI implements rate limiting.</p>

              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="border rounded-md p-4">
                    <h4 className="font-medium mb-2">Free Tier</h4>
                    <p className="text-sm text-gray-600">100 requests per day</p>
                    <p className="text-sm text-gray-600">5 requests per minute</p>
                  </div>

                  <div className="border rounded-md p-4">
                    <h4 className="font-medium mb-2">Pro Tier</h4>
                    <p className="text-sm text-gray-600">10,000 requests per day</p>
                    <p className="text-sm text-gray-600">100 requests per minute</p>
                  </div>

                  <div className="border rounded-md p-4">
                    <h4 className="font-medium mb-2">Enterprise Tier</h4>
                    <p className="text-sm text-gray-600">Unlimited requests</p>
                    <p className="text-sm text-gray-600">Custom rate limits</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="errors">
          <Card>
            <CardContent className="pt-6">
              <h3 className="text-lg font-medium mb-4">Error Handling</h3>
              <p className="mb-4">ToxidAPI uses standard HTTP status codes and returns detailed error messages.</p>

              <div className="space-y-4">
                <div>
                  <h4 className="text-sm font-medium mb-2">Error Response Format</h4>
                  <pre className="bg-gray-100 p-3 rounded-md text-sm overflow-x-auto">
                    {`{
  "error": {
    "code": "invalid_request",
    "message": "The request was invalid",
    "details": "Text field is required"
  }
}`}
                  </pre>
                </div>

                <div>
                  <h4 className="text-sm font-medium mb-2">Common Error Codes</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                    <div className="border rounded-md p-3">
                      <p className="font-medium">400 - Bad Request</p>
                      <p className="text-sm text-gray-600">Invalid request parameters</p>
                    </div>
                    <div className="border rounded-md p-3">
                      <p className="font-medium">401 - Unauthorized</p>
                      <p className="text-sm text-gray-600">Missing or invalid API key</p>
                    </div>
                    <div className="border rounded-md p-3">
                      <p className="font-medium">429 - Too Many Requests</p>
                      <p className="text-sm text-gray-600">Rate limit exceeded</p>
                    </div>
                    <div className="border rounded-md p-3">
                      <p className="font-medium">500 - Server Error</p>
                      <p className="text-sm text-gray-600">Internal server error</p>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

