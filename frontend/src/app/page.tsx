
"use client";

import { useEffect, useState, type ChangeEvent, type FormEvent } from "react";
import {
  Armchair,
  ImagePlus,
  Ruler,
  Sparkles,
  Wallet,
  X,
} from "lucide-react";
import axios from "axios";

export default function Home() {
  const [image, setImage] = useState<File | null>(null);
  const [preview, setPreview] = useState("");
  const [roomType, setRoomType] = useState("Bedroom");
  const [dimensions, setDimensions] = useState("");
  const [budget, setBudget] = useState("10000");
  const [currency, setCurrency] = useState("PKR");
  const [style, setStyle] = useState("Minimalist");
  const [furniture, setFurniture] = useState("");
  const [requirements, setRequirements] = useState("");
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  useEffect(() => {
    if (!image) {
      setPreview("");
      return;
    }

    const imageUrl = URL.createObjectURL(image);
    setPreview(imageUrl);

    return () => URL.revokeObjectURL(imageUrl);
  }, [image]);

  function handleImageChange(event: ChangeEvent<HTMLInputElement>) {
    const selectedFile = event.target.files?.[0];

    if (!selectedFile) return;

    if (!selectedFile.type.startsWith("image/")) {
      setMessage("Please select a valid image file.");
      event.target.value = "";
      return;
    }

    if (selectedFile.size > 10 * 1024 * 1024) {
      setMessage("Image size must be 10 MB or less.");
      event.target.value = "";
      return;
    }

    setMessage("");
    setImage(selectedFile);
  }

  
async function handleSubmit(event: FormEvent<HTMLFormElement>) {
  event.preventDefault();

  if (!image) {
    setMessage("Please upload a room image.");
    return;
  }

  setIsLoading(true);
  setMessage("");
  setResult(null);

  const formData = new FormData();

  formData.append("image", image);
  formData.append("room_type", roomType);
  formData.append("dimensions", dimensions);
  formData.append("budget", budget);
  formData.append("currency", currency);
  formData.append("style", style);
  formData.append("existing_furniture", furniture);
  formData.append("requirements", requirements);

  try {
    const response = await axios.post(
      `${process.env.NEXT_PUBLIC_API_URL}/api/design`,
      formData
    );

    setResult(response.data);
    setMessage("Your AI design has been generated successfully!");
  } catch (error) {
    console.error("Design request failed:", error);

    if (axios.isAxiosError(error)) {
      const detail = error.response?.data?.detail;

      setMessage(
        typeof detail === "string"
          ? detail
          : error.response
            ? `Request failed with status ${error.response.status}.`
            : "Could not connect to the backend. Check that FastAPI is running."
      );
    } else {
      setMessage("An unexpected error occurred. Please try again.");
    }
  } finally {
    setIsLoading(false);
  }
}


  function removeImage() {
    setImage(null);
    setMessage("");
  }

  return (
    <main className="min-h-screen bg-stone-100 text-slate-900">
      <header className="border-b border-stone-200 bg-white">
        <div className="mx-auto flex max-w-6xl items-center gap-3 px-5 py-5 sm:px-8">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-slate-900 text-white">
            <Armchair size={24} />
          </div>

          <div>
            <h1 className="text-xl font-bold tracking-tight">
              AI Home Decorator
            </h1>
            <p className="text-sm text-slate-500">
              A smarter way to design your space
            </p>
          </div>
        </div>
      </header>

      <section className="mx-auto max-w-6xl px-5 py-10 sm:px-8 sm:py-14">
        <div className="mb-10 max-w-2xl">
          <div className="mb-4 inline-flex items-center gap-2 rounded-full bg-amber-100 px-3 py-1.5 text-sm font-medium text-amber-900">
            <Sparkles size={16} />
            Personalized interior design
          </div>

          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
            Let's transform your room.
          </h2>

          <p className="mt-4 leading-7 text-slate-600">
            Share a photo, tell us about your space, and set your budget.
            Our AI design assistant will use these details to prepare
            personalized recommendations.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-8">
          <section className="rounded-2xl border border-stone-200 bg-white p-5 shadow-sm sm:p-8">
            <div className="mb-6">
              <h3 className="text-lg font-semibold">01. Your room photo</h3>
              <p className="mt-1 text-sm text-slate-500">
                Upload a clear photo of your current room. Maximum size: 10 MB.
              </p>
            </div>

            {!preview ? (
              <label
                htmlFor="room-image"
                className="flex min-h-64 cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed border-stone-300 bg-stone-50 px-5 py-10 text-center transition hover:border-slate-500 hover:bg-stone-100"
              >
                <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-white shadow-sm">
                  <ImagePlus size={28} className="text-slate-700" />
                </div>

                <span className="font-semibold">Upload your room image</span>
                <span className="mt-2 text-sm text-slate-500">
                  Click here to browse your files
                </span>

                <input
                  id="room-image"
                  type="file"
                  accept="image/*"
                  required
                  className="sr-only"
                  onChange={handleImageChange}
                />
              </label>
            ) : (
              <div className="relative overflow-hidden rounded-xl border border-stone-200">
                <img
                  src={preview}
                  alt="Preview of your room"
                  className="max-h-[420px] w-full object-contain bg-stone-100"
                />

                <button
                  type="button"
                  onClick={removeImage}
                  className="absolute right-3 top-3 flex items-center gap-2 rounded-lg bg-white px-3 py-2 text-sm font-medium shadow-md hover:bg-stone-100"
                >
                  <X size={16} />
                  Remove image
                </button>

                <div className="bg-white px-4 py-3 text-sm text-slate-600">
                  {image?.name}
                </div>
              </div>
            )}
          </section>

          <section className="rounded-2xl border border-stone-200 bg-white p-5 shadow-sm sm:p-8">
            <div className="mb-6">
              <h3 className="text-lg font-semibold">02. Tell us about your space</h3>
              <p className="mt-1 text-sm text-slate-500">
                Provide the basic details of your room.
              </p>
            </div>

            <div className="grid gap-5 sm:grid-cols-2">
              <div>
                <label htmlFor="room-type" className="mb-2 block text-sm font-medium">
                  Room type <span className="text-red-600">*</span>
                </label>
                <select
                  id="room-type"
                  value={roomType}
                  onChange={(e) => setRoomType(e.target.value)}
                  required
                  className="w-full rounded-xl border border-stone-300 bg-white px-4 py-3 outline-none focus:border-slate-600 focus:ring-2 focus:ring-slate-200"
                >
                  <option>Bedroom</option>
                  <option>Living Room</option>
                  <option>Kitchen</option>
                  <option>Dining Room</option>
                  <option>Home Office</option>
                  <option>Bathroom</option>
                  <option>Other</option>
                </select>
              </div>

              <div>
                <label htmlFor="dimensions" className="mb-2 block text-sm font-medium">
                  <Ruler size={16} className="mr-1 inline" />
                  Room dimensions <span className="text-red-600">*</span>
                </label>
                <input
                  id="dimensions"
                  value={dimensions}
                  onChange={(e) => setDimensions(e.target.value)}
                  placeholder="e.g. 10 × 12 ft"
                  required
                  className="w-full rounded-xl border border-stone-300 px-4 py-3 outline-none focus:border-slate-600 focus:ring-2 focus:ring-slate-200"
                />
              </div>

              <div>
                <label htmlFor="budget" className="mb-2 block text-sm font-medium">
                  <Wallet size={16} className="mr-1 inline" />
                  Total budget <span className="text-red-600">*</span>
                </label>
                <input
                  id="budget"
                  type="number"
                  min="1"
                  step="any"
                  value={budget}
                  onChange={(e) => setBudget(e.target.value)}
                  placeholder="Enter your budget"
                  required
                  className="w-full rounded-xl border border-stone-300 px-4 py-3 outline-none focus:border-slate-600 focus:ring-2 focus:ring-slate-200"
                />
              </div>

              <div>
                <label htmlFor="currency" className="mb-2 block text-sm font-medium">
                  Currency
                </label>
                <select
                  id="currency"
                  value={currency}
                  onChange={(e) => setCurrency(e.target.value)}
                  className="w-full rounded-xl border border-stone-300 bg-white px-4 py-3 outline-none focus:border-slate-600 focus:ring-2 focus:ring-slate-200"
                >
                  <option value="PKR">PKR — Pakistani Rupee</option>
                  <option value="USD">USD — US Dollar</option>
                  <option value="GBP">GBP — British Pound</option>
                  <option value="EUR">EUR — Euro</option>
                </select>
              </div>

              <div className="sm:col-span-2">
                <label htmlFor="style" className="mb-2 block text-sm font-medium">
                  Preferred design style <span className="text-red-600">*</span>
                </label>
                <select
                  id="style"
                  value={style}
                  onChange={(e) => setStyle(e.target.value)}
                  required
                  className="w-full rounded-xl border border-stone-300 bg-white px-4 py-3 outline-none focus:border-slate-600 focus:ring-2 focus:ring-slate-200"
                >
                  <option>Minimalist</option>
                  <option>Modern</option>
                  <option>Contemporary</option>
                  <option>Scandinavian</option>
                  <option>Industrial</option>
                  <option>Traditional</option>
                  <option>Bohemian</option>
                  <option>Luxury</option>
                  <option>Not sure — recommend a style</option>
                </select>
              </div>
            </div>
          </section>

          <section className="rounded-2xl border border-stone-200 bg-white p-5 shadow-sm sm:p-8">
            <div className="mb-6">
              <h3 className="text-lg font-semibold">03. Your preferences</h3>
              <p className="mt-1 text-sm text-slate-500">
                Help the AI understand what you want to keep and improve.
              </p>
            </div>

            <div className="space-y-5">
              <div>
                <label htmlFor="furniture" className="mb-2 block text-sm font-medium">
                  Existing furniture <span className="text-red-600">*</span>
                </label>
                <textarea
                  id="furniture"
                  value={furniture}
                  onChange={(e) => setFurniture(e.target.value)}
                  placeholder="e.g. Bed, wardrobe, study table. I want to keep them."
                  rows={3}
                  required
                  className="w-full resize-y rounded-xl border border-stone-300 px-4 py-3 outline-none focus:border-slate-600 focus:ring-2 focus:ring-slate-200"
                />
              </div>

              <div>
                <label htmlFor="requirements" className="mb-2 block text-sm font-medium">
                  What would you like to improve?{" "}
                  <span className="text-red-600">*</span>
                </label>
                <textarea
                  id="requirements"
                  value={requirements}
                  onChange={(e) => setRequirements(e.target.value)}
                  placeholder="e.g. More storage, better lighting, a modern look, and clear walking space."
                  rows={4}
                  required
                  className="w-full resize-y rounded-xl border border-stone-300 px-4 py-3 outline-none focus:border-slate-600 focus:ring-2 focus:ring-slate-200"
                />
              </div>
            </div>
          </section>

          {message && (
            <p
              role="status"
              className="rounded-xl border border-slate-200 bg-white p-4 text-sm text-slate-700"
            >
              {message}
            </p>
          )}

          <div className="flex flex-col items-start justify-between gap-4 rounded-2xl bg-slate-900 p-6 text-white sm:flex-row sm:items-center sm:p-8">
            <div>
              <h3 className="font-semibold">Ready to plan your room?</h3>
              <p className="mt-1 text-sm text-slate-300">
                Review your details before continuing.
              </p>
            </div>

            
            <button
              type="submit"
              disabled={isLoading}
              className="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-amber-300 px-6 py-3 font-semibold text-slate-900 transition hover:bg-amber-200 disabled:cursor-not-allowed disabled:opacity-60 sm:w-auto"
            >
              <Sparkles size={18} />
              {isLoading ? "Analyzing your room..." : "Generate Design"}
            </button>

          </div>
        </form>
        {result && (
          <section className="mt-8 rounded-2xl border border-stone-200 bg-white p-5 shadow-sm sm:p-8">
            <h2 className="text-xl font-bold">
              AI Design Results
            </h2>

            <p className="mt-2 text-sm text-slate-600">
              Your backend returned the following design information.
            </p>

            <pre className="mt-5 max-h-[600px] overflow-auto rounded-xl bg-slate-950 p-4 text-sm leading-6 text-green-300">
              {JSON.stringify(result, null, 2)}
            </pre>
          </section>
        )}
      </section>
    </main>
  );
}
