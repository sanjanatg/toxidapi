import type React from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { AlertCircle, BarChart, Bot, Clock, Code, Database, FileText, Shield, Zap } from "lucide-react"

export default function Features() {
  return (
    <div className="space-y-6">
      <div className="prose max-w-none">
        <h2>ToxidAPI Features</h2>
        <p>
          ToxidAPI is a sophisticated text analysis API powered by Google&apos;s Gemini AI that provides comprehensive
          content moderation capabilities.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <FeatureCard
          icon={<AlertCircle className="h-8 w-8 text-red-500" />}
          title="Toxicity Detection"
          description="Identify toxic content with detailed category scoring to keep your platform safe and welcoming."
        />

        <FeatureCard
          icon={<BarChart className="h-8 w-8 text-blue-500" />}
          title="Sentiment Analysis"
          description="Understand the emotional tone of text with accurate sentiment scoring and labeling."
        />

        <FeatureCard
          icon={<Shield className="h-8 w-8 text-green-500" />}
          title="Content Moderation"
          description="Automatically identify and flag inappropriate content with detailed word-level analysis."
        />

        <FeatureCard
          icon={<FileText className="h-8 w-8 text-purple-500" />}
          title="Content Categorization"
          description="Categorize inappropriate content into specific types for more granular moderation."
        />

        <FeatureCard
          icon={<Zap className="h-8 w-8 text-yellow-500" />}
          title="High Performance"
          description="Fast processing times with optimized algorithms for real-time content moderation."
        />

        <FeatureCard
          icon={<Database className="h-8 w-8 text-indigo-500" />}
          title="Batch Processing"
          description="Analyze multiple texts in a single API call for efficient processing of large datasets."
        />

        <FeatureCard
          icon={<Clock className="h-8 w-8 text-orange-500" />}
          title="Rate Limiting"
          description="Configurable rate limits to ensure fair usage and system stability."
        />

        <FeatureCard
          icon={<Bot className="h-8 w-8 text-teal-500" />}
          title="Gemini AI Powered"
          description="Leverages Google's advanced Gemini AI models for state-of-the-art text analysis."
        />

        <FeatureCard
          icon={<Code className="h-8 w-8 text-gray-500" />}
          title="SDK Support"
          description="Official SDKs for JavaScript, Python, Node.js, and React for easy integration."
        />
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="text-xl font-bold text-blue-800 mb-4">Why Choose ToxidAPI?</h3>
        <ul className="space-y-2">
          <li className="flex items-start">
            <span className="text-blue-500 mr-2">✓</span>
            <span>Advanced AI models trained on diverse content for accurate detection</span>
          </li>
          <li className="flex items-start">
            <span className="text-blue-500 mr-2">✓</span>
            <span>Comprehensive analysis with multiple detection categories</span>
          </li>
          <li className="flex items-start">
            <span className="text-blue-500 mr-2">✓</span>
            <span>Fast processing times for real-time applications</span>
          </li>
          <li className="flex items-start">
            <span className="text-blue-500 mr-2">✓</span>
            <span>Detailed reporting with word-level analysis</span>
          </li>
          <li className="flex items-start">
            <span className="text-blue-500 mr-2">✓</span>
            <span>Easy integration with popular programming languages</span>
          </li>
          <li className="flex items-start">
            <span className="text-blue-500 mr-2">✓</span>
            <span>Scalable infrastructure for projects of any size</span>
          </li>
        </ul>
      </div>
    </div>
  )
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode; title: string; description: string }) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="mb-2">{icon}</div>
        <CardTitle className="text-lg">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <CardDescription className="text-gray-600">{description}</CardDescription>
      </CardContent>
    </Card>
  )
}

