"use client"

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export default function SdkExamples() {
  return (
    <div className="space-y-6">
      <div className="prose max-w-none">
        <h2>SDK Examples</h2>
        <p>
          ToxidAPI provides SDKs for popular programming languages to make integration easier. Below are examples of how
          to use our SDKs in different languages.
        </p>
      </div>

      <Tabs defaultValue="javascript">
        <TabsList>
          <TabsTrigger value="javascript">JavaScript</TabsTrigger>
          <TabsTrigger value="python">Python</TabsTrigger>
          <TabsTrigger value="nodejs">Node.js</TabsTrigger>
          <TabsTrigger value="react">React</TabsTrigger>
        </TabsList>

        <TabsContent value="javascript" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>JavaScript SDK Example</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <h4 className="text-sm font-medium mb-2">Installation</h4>
                  <pre className="bg-gray-100 p-3 rounded-md text-sm overflow-x-auto">
                    {`npm install toxid-api-js
// or
yarn add toxid-api-js`}
                  </pre>
                </div>

                <div>
                  <h4 className="text-sm font-medium mb-2">Basic Usage</h4>
                  <pre className="bg-gray-100 p-3 rounded-md text-sm overflow-x-auto">
                    {`import { ToxidAPI } from 'toxid-api-js';

// Initialize the client
const toxid = new ToxidAPI('YOUR_API_KEY');

// Analyze text
async function analyzeText() {
  try {
    const result = await toxid.analyze('Text to analyze');
    console.log(result);
    
    // Check if text is toxic
    if (result.toxicity.isToxic) {
      console.log('Warning: Toxic content detected!');
    }
    
    // Get sentiment
    console.log(\`Sentiment: \${result.sentiment.label}\`);
    
    // Check flagged words
    if (result.flaggedWords.count > 0) {
      console.log(\`Flagged words: \${result.flaggedWords.words.join(', ')}\`);
    }
  } catch (error) {
    console.error('Error analyzing text:', error);
  }
}`}
                  </pre>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="python" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Python SDK Example</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <h4 className="text-sm font-medium mb-2">Installation</h4>
                  <pre className="bg-gray-100 p-3 rounded-md text-sm overflow-x-auto">{`pip install toxid-api`}</pre>
                </div>

                <div>
                  <h4 className="text-sm font-medium mb-2">Basic Usage</h4>
                  <pre className="bg-gray-100 p-3 rounded-md text-sm overflow-x-auto">
                    {`from toxid_api import ToxidAPI

# Initialize the client
toxid = ToxidAPI('YOUR_API_KEY')

# Analyze text
def analyze_text():
    try:
        result = toxid.analyze('Text to analyze')
        print(result)
        
        # Check if text is toxic
        if result['toxicity']['isToxic']:
            print('Warning: Toxic content detected!')
        
        # Get sentiment
        print(f"Sentiment: {result['sentiment']['label']}")
        
        # Check flagged words
        if result['flaggedWords']['count'] > 0:
            print(f"Flagged words: {', '.join(result['flaggedWords']['words'])}")
    except Exception as e:
        print(f"Error analyzing text: {e}")

# Batch analysis
def analyze_batch():
    texts = [
        "This is the first text to analyze",
        "This is the second text to analyze"
    ]
    results = toxid.analyze_batch(texts)
    for i, result in enumerate(results):
        print(f"Result {i+1}:")
        print(result)

if __name__ == "__main__":
    analyze_text()
    analyze_batch()`}
                  </pre>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="nodejs" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Node.js SDK Example</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <h4 className="text-sm font-medium mb-2">Installation</h4>
                  <pre className="bg-gray-100 p-3 rounded-md text-sm overflow-x-auto">
                    {`npm install toxid-api-node
// or
yarn add toxid-api-node`}
                  </pre>
                </div>

                <div>
                  <h4 className="text-sm font-medium mb-2">Express.js Integration</h4>
                  <pre className="bg-gray-100 p-3 rounded-md text-sm overflow-x-auto">
                    {`const express = require('express');
const { ToxidAPI } = require('toxid-api-node');

const app = express();
app.use(express.json());

// Initialize the client
const toxid = new ToxidAPI('YOUR_API_KEY');

// Create a content moderation middleware
const moderateContent = async (req, res, next) => {
  try {
    const { content } = req.body;
    
    if (!content) {
      return next();
    }
    
    const result = await toxid.analyze(content);
    
    // Attach the analysis result to the request
    req.contentAnalysis = result;
    
    // Block toxic content if needed
    if (result.toxicity.isToxic && result.toxicity.score > 0.8) {
      return res.status(400).json({
        error: 'Content moderation failed',
        message: 'The submitted content contains inappropriate language'
      });
    }
    
    next();
  } catch (error) {
    console.error('Content moderation error:', error);
    next();
  }
};

// Apply the middleware to routes that need content moderation
app.post('/comments', moderateContent, (req, res) => {
  // Process the comment
  // req.contentAnalysis contains the analysis result
  res.json({ success: true });
});

app.listen(3000, () => {
  console.log('Server running on port 3000');
});`}
                  </pre>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="react" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>React Integration Example</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <h4 className="text-sm font-medium mb-2">Installation</h4>
                  <pre className="bg-gray-100 p-3 rounded-md text-sm overflow-x-auto">
                    {`npm install toxid-api-react
// or
yarn add toxid-api-react`}
                  </pre>
                </div>

                <div>
                  <h4 className="text-sm font-medium mb-2">React Component Example</h4>
                  <pre className="bg-gray-100 p-3 rounded-md text-sm overflow-x-auto">
                    {`import React, { useState } from 'react';
import { useToxidAnalysis } from 'toxid-api-react';

function CommentForm() {
  const [comment, setComment] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { analyze, isLoading, error } = useToxidAnalysis('YOUR_API_KEY');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    try {
      // Analyze the comment before submitting
      const result = await analyze(comment);
      
      // Check if the comment is appropriate
      if (result.toxicity.isToxic) {
        alert('Your comment contains inappropriate language. Please revise it.');
        setIsSubmitting(false);
        return;
      }
      
      // If the comment passes moderation, submit it
      // ... submit logic here
      
      // Reset form
      setComment('');
      alert('Comment submitted successfully!');
    } catch (err) {
      console.error('Error:', err);
      alert('An error occurred while submitting your comment.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="mb-4">
        <label htmlFor="comment" className="block mb-2">
          Add a comment:
        </label>
        <textarea
          id="comment"
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          className="w-full p-2 border rounded"
          rows={4}
          disabled={isLoading || isSubmitting}
        />
      </div>
      
      {error && (
        <div className="text-red-500 mb-4">
          Error: {error.message}
        </div>
      )}
      
      <button
        type="submit"
        className="px-4 py-2 bg-blue-500 text-white rounded"
        disabled={!comment || isLoading || isSubmitting}
      >
        {isLoading || isSubmitting ? 'Processing...' : 'Submit Comment'}
      </button>
    </form>
  );
}`}
                  </pre>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

