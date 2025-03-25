"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Clock } from "lucide-react"
import SampleTexts from "@/components/sample-texts"

// Mock API response type
interface AnalysisResult {
  text: string
  toxicity: {
    score: number
    isToxic: boolean
  }
  sentiment: {
    score: number
    label: "POSITIVE" | "NEGATIVE" | "NEUTRAL"
  }
  flaggedWords: {
    count: number
    severity: number
    words: string[]
    categories: {
      name: string
      words: string[]
    }[]
  }
  processingTime: number
}

export default function DemoInterface() {
  const [text, setText] = useState("")
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [result, setResult] = useState<AnalysisResult | null>(null)

  const handleAnalyze = async () => {
    if (!text.trim()) return

    setIsAnalyzing(true)

    // Simulate API call with mock data
    // In a real implementation, you would call your actual API endpoint
    setTimeout(() => {
      // Mock response based on input text
      const isToxic =
        text.toLowerCase().includes("shit") ||
        text.toLowerCase().includes("f*ck") ||
        text.toLowerCase().includes("hate")

      const mockResult: AnalysisResult = {
        text,
        toxicity: {
          score: isToxic ? 0.9 : 0.1,
          isToxic: isToxic,
        },
        sentiment: {
          score: isToxic ? 0.1 : 0.8,
          label: isToxic ? "NEGATIVE" : "POSITIVE",
        },
        flaggedWords: {
          count: isToxic ? 2 : 0,
          severity: isToxic ? 0.8 : 0,
          words: isToxic ? ["f*cking", "shit"] : [],
          categories: isToxic
            ? [
                {
                  name: "Profanity",
                  words: ["f*cking", "shit"],
                },
              ]
            : [],
        },
        processingTime: Math.random() * 3 + 0.5,
      }

      setResult(mockResult)
      setIsAnalyzing(false)
    }, 1500)
  }

  const handleClear = () => {
    setText("")
    setResult(null)
  }

  const handleSampleClick = (sampleText: string) => {
    setText(sampleText)
    setResult(null)
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-md shadow">
        <div className="bg-blue-600 text-white p-4 rounded-t-md">
          <h2 className="text-xl font-bold">ToxidAPI Demo</h2>
        </div>

        <div className="p-4">
          <div className="mb-4">
            <label htmlFor="text-input" className="block text-sm font-medium text-gray-700 mb-1">
              Enter text to analyze:
            </label>
            <Textarea
              id="text-input"
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Type or paste text here to analyze for toxicity, sentiment, and inappropriate content..."
              className="min-h-[120px]"
            />
          </div>

          <div className="flex space-x-2">
            <Button
              onClick={handleAnalyze}
              disabled={!text.trim() || isAnalyzing}
              className="bg-blue-600 hover:bg-blue-700"
            >
              {isAnalyzing ? "Analyzing..." : "Analyze"}
            </Button>
            <Button onClick={handleClear} variant="outline" className="text-gray-600">
              Clear
            </Button>
          </div>
        </div>
      </div>

      {result && (
        <div className="bg-red-50 border border-red-200 rounded-md">
          <div className="p-4 border-b border-red-200">
            <h3 className="text-lg font-semibold text-gray-800">Analysis Results</h3>
          </div>

          <div className="p-4">
            <div className="mb-4">
              <span className="font-medium">Text:</span> {result.text}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-base">Toxicity</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div>
                      <span className="text-sm text-gray-500">Score:</span>{" "}
                      <span className="font-semibold">{result.toxicity.score.toFixed(4)}</span>
                    </div>
                    <div>
                      <span className="text-sm text-gray-500">Is Toxic:</span>{" "}
                      <span className={`font-semibold ${result.toxicity.isToxic ? "text-red-600" : "text-green-600"}`}>
                        {result.toxicity.isToxic ? "true" : "false"}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-base">Sentiment</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div>
                      <span className="text-sm text-gray-500">Score:</span>{" "}
                      <span className="font-semibold">{result.sentiment.score.toFixed(4)}</span>
                    </div>
                    <div>
                      <span className="text-sm text-gray-500">Label:</span>{" "}
                      <span
                        className={`font-semibold ${
                          result.sentiment.label === "POSITIVE"
                            ? "text-green-600"
                            : result.sentiment.label === "NEGATIVE"
                              ? "text-red-600"
                              : "text-yellow-600"
                        }`}
                      >
                        {result.sentiment.label}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-base">Flagged Words</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div>
                      <span className="text-sm text-gray-500">Count:</span>{" "}
                      <span className="font-semibold">{result.flaggedWords.count}</span>
                    </div>
                    {result.flaggedWords.count > 0 && (
                      <>
                        <div>
                          <span className="text-sm text-gray-500">Severity:</span>{" "}
                          <span className="font-semibold text-red-600">
                            {result.flaggedWords.severity.toFixed(2)} (High)
                          </span>
                        </div>
                        <div>
                          <span className="text-sm text-gray-500">Words:</span>{" "}
                          <span className="font-semibold text-red-600">{result.flaggedWords.words.join(", ")}</span>
                        </div>
                      </>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>

            {result.flaggedWords.categories.length > 0 && (
              <div className="mb-4">
                <h4 className="text-sm font-medium text-gray-700 mb-2">Categories:</h4>
                <div className="flex flex-wrap gap-2">
                  {result.flaggedWords.categories.map((category, index) => (
                    <Badge key={index} variant="destructive" className="px-2 py-1">
                      {category.name}: {category.words.join(", ")}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            <div className="text-sm text-gray-500 flex items-center">
              <Clock className="h-4 w-4 mr-1" />
              Processing Time: {result.processingTime.toFixed(4)} seconds
            </div>
          </div>
        </div>
      )}

      <SampleTexts onSampleClick={handleSampleClick} />
    </div>
  )
}

