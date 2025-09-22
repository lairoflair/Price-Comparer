import React from "react";

export default function MainPart() {
  return (
    <div className="flex min-h-screen">
      {/* Left Sidebar */}
      <div className="w-48 bg-gray-200 p-4">
        <div className="sticky top-4 space-y-4">
          <div className="bg-gray-400 h-32 flex items-center justify-center">Ad 1</div>
          <div className="bg-gray-400 h-32 flex items-center justify-center">Ad 2</div>
        </div>
      </div>

      {/* Center Product Grid */}
      <div className="flex-1 p-4">
        <div className="grid grid-cols-3 gap-4">
          {[...Array(12)].map((_, i) => (
            <div key={i} className="bg-gray-300 h-40 flex items-center justify-center">
              Product {i + 1}
            </div>
          ))}
        </div>
      </div>

      {/* Right Sidebar */}
      <div className="w-48 bg-gray-200 p-4">
        <div className="sticky top-4 space-y-4">
          <div className="bg-gray-400 h-32 flex items-center justify-center">Ad 3</div>
          <div className="bg-gray-400 h-32 flex items-center justify-center">Ad 4</div>
        </div>
      </div>
    </div>
  );
}
