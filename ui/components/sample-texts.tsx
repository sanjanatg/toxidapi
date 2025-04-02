"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"

interface SampleTextsProps {
  onSampleClick: (text: string) => void
}

const samples = [
  {
    text: "This product is amazing! I love it so much.",
    type: "positive",
  },
  {
    text: "I hate this product. It's terrible and doesn't work.",
    type: "negative",
  },
  {
    text: "This f*cking product is shit.",
    type: "toxic",
  },
  {
    text: "The customer service was helpful but the product is average.",
    type: "neutral",
  },
]

export default function SampleTexts({ onSampleClick }: SampleTextsProps) {
  return (
    <Card>
      <CardHeader className="bg-cyan-500 text-white rounded-t-md">
        <CardTitle>Sample Texts</CardTitle>
      </CardHeader>
      <CardContent className="p-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
          {samples.map((sample, index) => (
            <Button
              key={index}
              variant="outline"
              className="justify-start h-auto py-2 px-3 text-left"
              onClick={() => onSampleClick(sample.text)}
            >
              {sample.text}
            </Button>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

