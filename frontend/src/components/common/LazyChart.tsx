import React, { useState, useEffect, Suspense, lazy, ReactNode } from 'react';

interface LazyChartProps {
  children: ReactNode;
  height?: string | number;
  width?: string | number;
  fallback?: ReactNode;
  loadDelay?: number;
}

/**
 * A wrapper component that lazy loads its children only when they become visible
 * in the viewport. Useful for performance optimization of charts and graphs.
 */
const LazyChart: React.FC<LazyChartProps> = ({
  children,
  height = '300px',
  width = '100%',
  fallback,
  loadDelay = 100
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [inViewport, setInViewport] = useState(false);
  const [ref, setRef] = useState<HTMLDivElement | null>(null);

  useEffect(() => {
    // If we already determined it's visible, no need to check again
    if (isVisible) return;

    // Create intersection observer to detect when chart is in viewport
    const observer = new IntersectionObserver(
      ([entry]) => {
        setInViewport(entry.isIntersecting);
      },
      {
        root: null,
        rootMargin: '0px',
        threshold: 0.1 // Trigger when at least 10% is visible
      }
    );

    // Start observing when ref is available
    if (ref) {
      observer.observe(ref);
    }

    // Cleanup
    return () => {
      if (ref) {
        observer.unobserve(ref);
      }
    };
  }, [ref, isVisible]);

  // Delay rendering slightly after entering viewport
  // This prevents jank when scrolling quickly
  useEffect(() => {
    if (!inViewport || isVisible) return;
    
    const timer = setTimeout(() => {
      setIsVisible(true);
    }, loadDelay);
    
    return () => clearTimeout(timer);
  }, [inViewport, isVisible, loadDelay]);

  // Default fallback is a placeholder with same dimensions
  const defaultFallback = (
    <div 
      className="flex items-center justify-center bg-gray-100 dark:bg-gray-700 rounded animate-pulse"
      style={{ height, width }}
    >
      <svg className="w-12 h-12 text-gray-300 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 13v-1m4 1v-3m4 3V8M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
      </svg>
    </div>
  );

  return (
    <div ref={setRef} style={{ height, width }}>
      {isVisible ? children : (fallback || defaultFallback)}
    </div>
  );
};

export default LazyChart; 