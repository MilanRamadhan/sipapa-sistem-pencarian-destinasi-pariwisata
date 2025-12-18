"use client";

import { useState } from "react";

interface SafeImageProps {
  src: string;
  alt: string;
  className?: string;
  fill?: boolean;
  sizes?: string;
  priority?: boolean;
}

export default function SafeImage({ src, alt, className, fill, sizes, priority }: SafeImageProps) {
  const [error, setError] = useState(false);

  if (error || !src) {
    return null;
  }

  return <img src={src} alt={alt} className={className} onError={() => setError(true)} />;
}
