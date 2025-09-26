"use client";
import { useState } from "react";
import ContainerWrapper from "./containerWrapper";
import search from "@/assets/icons/search.png";
import PrimaryButton from "./primaryButton";
import { Menu, X } from "lucide-react";
import Image from "next/image";
import facebookLogo from "@/assets/icons/facebook.svg";

const PublicHeader = () => {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <header className=" w-full  bg-white ">
      <ContainerWrapper>
        <div className="flex items-center justify-between py-3">
          <div className="flex items-center gap-2">
            <Image src={facebookLogo} alt="facebook" width={60} height={40} />
            <p className="font-bold text-gray-600 text-lg sm:text-xl lg:text-2xl">
              Facebook
            </p>
          </div>
          <nav className="hidden md:block">
            <ul className="flex gap-4 lg:gap-6 font-medium text-gray-700 text-sm sm:text-base">
              <li className="cursor-pointer hover:text-blue-600">Home</li>
              <li className="cursor-pointer hover:text-blue-600">Categories</li>
              <li className="cursor-pointer hover:text-blue-600">
                My Learning
              </li>
              <li className="cursor-pointer hover:text-blue-600">Wishlist</li>
            </ul>
          </nav>
          <div className="hidden lg:flex items-center gap-3 xl:gap-4">
            <div className="flex items-center gap-2 rounded-lg px-2 py-1 bg-gray-100">
              <input
                type="text"
                placeholder="Search"
                className="outline-none text-sm lg:text-base w-32 xl:w-48"
              />
              <Image src={search} alt="Search" width={18} height={18} />
            </div>
            <PrimaryButton className="bg-blue-600 rounded-[10px] hover:bg-gray-400 px-3 py-1 text-sm lg:px-4 lg:py-2">
              Sign Up
            </PrimaryButton>
            <PrimaryButton className="bg-blue-200 text-blue-500  rounded-[10px] hover:bg-gray-400 px-3 py-1 text-sm lg:px-4 lg:py-2">
              Log in
            </PrimaryButton>
          </div>
          <PrimaryButton
            className="lg:hidden md:hidden"
            onClick={() => setMenuOpen(!menuOpen)}
          >
            {menuOpen ? <X size={28} /> : <Menu size={28} />}
          </PrimaryButton>
        </div>
        {menuOpen && (
          <div className="lg:hidden md:hidden mt-11 w-full h-screen flex flex-col gap-6 items-center">
            <ul className="flex flex-col items-center gap-4 font-medium text-gray-700 text-lg">
              <li className="cursor-pointer hover:text-blue-600">Home</li>
              <li className="cursor-pointer hover:text-blue-600">Categories</li>
              <li className="cursor-pointer hover:text-blue-600">
                My Learning
              </li>
              <li className="cursor-pointer hover:text-blue-600">Wishlist</li>
            </ul>
            <div className="flex flex-col gap-3 w-3/4">
              <PrimaryButton className="bg-blue-600 w-full  rounded-[10px] hover:bg-gray-400 py-2 text-white">
                Sign Up
              </PrimaryButton>
              <PrimaryButton className="bg-blue-300 w-full rounded-[10px] hover:bg-gray-400 py-2 text-blue-700">
                Log in
              </PrimaryButton>
            </div>
          </div>
        )}
      </ContainerWrapper>
    </header>
  );
};

export default PublicHeader;
