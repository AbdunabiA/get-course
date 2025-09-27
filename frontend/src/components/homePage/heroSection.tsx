"use client";
import React from "react";
import PrimaryButton from "@/components/ui/primaryButton";

const HeroSection = () => {
  return (
    <section>
      <div className="w-full bg-[url('@/assets/images/bgImagesCourse.jpg')] h-screen bg-cover bg-center flex items-center justify-center">
        <div className="text-center max-w-2xl px-4">
          <h1 className="text-3xl md:text-5xl font-bold text-white mb-4">
            Expand your career with EduHud
          </h1>
          <p className="text-sm md:text-lg text-gray-200 mb-6">
            Explore a wide range of courses taught by industry experts. Learn at
            your own pace and achieve your professional goals
          </p>
          <div className="flex items-center bg-white rounded-lg overflow-hidden shadow-md w-full md:w-[500px] mx-auto">
            <input
              type="text"
              placeholder="What do you want to learn?"
              className="flex-1 px-2 py-4 text-gray-700 focus:outline-none"
            />
            <PrimaryButton className="px-6 py-4 bg-blue-600 text-white font-medium hover:bg-blue-700 transition">
              Search
            </PrimaryButton>
          </div>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;
