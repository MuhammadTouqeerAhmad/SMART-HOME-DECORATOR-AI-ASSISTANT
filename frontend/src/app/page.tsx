
"use client";

import { useEffect, useState, type ChangeEvent, type FormEvent } from "react";
import axios from "axios";
import {
  Armchair,
  CheckCircle2,
  CircleDollarSign,
  ImagePlus,
  Lightbulb,
  LoaderCircle,
  Package,
  Palette,
  Ruler,
  Sparkles,
  TriangleAlert,
  Wallet,
  X,
} from "lucide-react";

type ResultData = Record<string, any>;

function getField(data: ResultData | undefined, keys: string[]) {
  if (!data || typeof data !== "object") return undefined;

  for (const key of keys) {
    const value = data[key];

    if (value !== undefined && value !== null && value !== "") {
      return value;
    }
  }

  return undefined;
}

function displayText(value: any): string {
  if (value === undefined || value === null || value === "") return "";

  if (typeof value === "string" || typeof value === "number") {
    return String(value);
  }

  if (typeof value === "boolean") {
    return value ? "Yes" : "No";
  }

  if (Array.isArray(value)) {
    return value.map(displayText).filter(Boolean).join(", ");
  }

  return "";
}

function formatMoney(value: any, currency: string) {
  if (value === undefined || value === null || value === "") {
    return "Not available";
  }

  const amount = Number(value);

  if (!Number.isFinite(amount)) {
    return String(value);
  }

  return `${currency} ${amount.toLocaleString("en-US", {
    maximumFractionDigits: 2,
  })}`;
}

function getItems(value: any): any[] {
  if (Array.isArray(value)) return value;
  if (value && typeof value === "object") return Object.values(value);
  if (typeof value === "string" && value.trim()) return [value];
  return [];
}

function ResultList({ value }: { value: any }) {
  const items = getItems(value);

  if (items.length === 0) {
    return (
      <p className="text-sm text-slate-500">
        No additional details available.
      </p>
    );
  }

  return (
    <ul className="space-y-3">
      {items.map((item, index) => {
        const text =
          typeof item === "object" && item !== null
            ? displayText(
                getField(item, ["name", "description", "title", "reason"])
              ) || JSON.stringify(item)
            : displayText(item);

        return (
          <li key={index} className="flex items-start gap-3">
            <span className="mt-2 h-2 w-2 shrink-0 rounded-full bg-amber-500" />
            <span className="text-sm leading-6 text-slate-600">{text}</span>
          </li>
        );
      })}
    </ul>
  );
}

function ResultCard({
  title,
  description,
  icon,
  children,
}: {
  title: string;
  description: string;
  icon: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <section className="rounded-2xl border border-stone-200 bg-white p-5 shadow-sm sm:p-7">
      <div className="mb-5 flex items-start gap-3">
        <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-amber-100 text-amber-900">
          {icon}
        </div>
        <div>
          <h3 className="text-lg font-bold text-slate-900">{title}</h3>
          <p className="mt-1 text-sm leading-6 text-slate-500">
            {description}
          </p>
        </div>
      </div>
      {children}
    </section>
  );
}

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
  const [result, setResult] = useState<ResultData | null>(null);

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
      setMessage("Your image must be 10 MB or less.");
      event.target.value = "";
      return;
    }

    setImage(selectedFile);
    setMessage("");
    setResult(null);
  }

  function removeImage() {
    setImage(null);
    setResult(null);
    setMessage("");
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!image) {
      setMessage("Please upload a photo of your room.");
      return;
    }

    if (!Number.isFinite(Number(budget)) || Number(budget) <= 0) {
      setMessage("Please enter a valid budget greater than zero.");
      return;
    }

    const apiUrl = process.env.NEXT_PUBLIC_API_URL;

    if (!apiUrl) {
      setMessage(
        "The backend URL is not configured. Check frontend/.env.local."
      );
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
        `${apiUrl.replace(/\/+$/, "")}/api/design`,
        formData
      );

      setResult(response.data);
      setMessage("Your personalized design is ready.");
    } catch (error) {
      console.error("Design request failed:", error);

      if (axios.isAxiosError(error)) {
        const detail = error.response?.data?.detail;

        setMessage(
          typeof detail === "string"
            ? detail
            : error.response
              ? `The request failed (HTTP ${error.response.status}). Please try again.`
              : "Unable to connect to the backend. Make sure FastAPI is running."
        );
      } else {
        setMessage("Something went wrong. Please try again.");
      }
    } finally {
      setIsLoading(false);
    }
  }

  const analysis = result?.room_analysis ?? {};
  const strategy = result?.design_strategy ?? {};
  const budgetInfo = result?.budget_result ?? {};

  const products: ResultData[] = Array.isArray(result?.selected_products)
    ? result.selected_products
    : [];

  const roomFurniture = getField(analysis, [
    "visible_furniture",
    "furniture",
    "existing_furniture",
  ]);

  const roomColors = getField(analysis, [
    "colors",
    "color_palette",
    "dominant_colors",
  ]);

  const roomLighting = getField(analysis, [
    "lighting",
    "natural_light",
    "lighting_conditions",
  ]);

  const roomIssues = getField(analysis, [
    "issues",
    "problems",
    "improvement_areas",
    "challenges",
  ]);

  const roomOpportunities = getField(analysis, [
    "opportunities",
    "suggestions",
    "design_opportunities",
  ]);

  const priorities = getField(strategy, [
    "improvement_priorities",
    "priorities",
  ]);

  const designOverview = displayText(
    getField(strategy, [
      "summary",
      "overview",
      "design_concept",
      "description",
    ])
  );

  const totalCost = getField(budgetInfo, [
    "total_cost",
    "total",
    "estimated_total",
    "selected_total",
  ]);

  const remainingBudget = getField(budgetInfo, [
    "remaining_budget",
    "remaining",
    "budget_remaining",
  ]);

  const withinBudget = getField(budgetInfo, [
    "within_budget",
    "is_within_budget",
  ]);

  const resultCurrency =
    displayText(getField(budgetInfo, ["currency"])) || currency;

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
            Let&apos;s transform your room.
          </h2>

          <p className="mt-4 leading-7 text-slate-600">
            Share a photo, tell us about your space, and set your budget.
            Our AI design assistant will prepare recommendations tailored
            to your room and preferences.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-8">
          {/* ROOM PHOTO */}
          <section className="rounded-2xl border border-stone-200 bg-white p-5 shadow-sm sm:p-8">
            <div className="mb-6">
              <h3 className="text-lg font-semibold">01. Your room photo</h3>
              <p className="mt-1 text-sm text-slate-500">
                Upload a clear image of your room. Maximum size: 10 MB.
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
                  className="max-h-[420px] w-full bg-stone-100 object-contain"
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

          {/* ROOM DETAILS */}
          <section className="rounded-2xl border border-stone-200 bg-white p-5 shadow-sm sm:p-8">
            <div className="mb-6">
              <h3 className="text-lg font-semibold">
                02. Tell us about your space
              </h3>
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
                  onChange={(event) => setRoomType(event.target.value)}
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
                  onChange={(event) => setDimensions(event.target.value)}
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
                  onChange={(event) => setBudget(event.target.value)}
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
                  onChange={(event) => setCurrency(event.target.value)}
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
                  onChange={(event) => setStyle(event.target.value)}
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

          {/* PREFERENCES */}
          <section className="rounded-2xl border border-stone-200 bg-white p-5 shadow-sm sm:p-8">
            <div className="mb-6">
              <h3 className="text-lg font-semibold">03. Your preferences</h3>
              <p className="mt-1 text-sm text-slate-500">
                Tell the AI what you want to keep and improve.
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
                  onChange={(event) => setFurniture(event.target.value)}
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
                  onChange={(event) => setRequirements(event.target.value)}
                  placeholder="e.g. More storage, better lighting, a modern look, and clear walking space."
                  rows={4}
                  required
                  className="w-full resize-y rounded-xl border border-stone-300 px-4 py-3 outline-none focus:border-slate-600 focus:ring-2 focus:ring-slate-200"
                />
              </div>
            </div>
          </section>

          {/* STATUS */}
          {message && (
            <div
              role="status"
              className={`rounded-xl border p-4 text-sm ${
                result
                  ? "border-emerald-200 bg-emerald-50 text-emerald-900"
                  : isLoading
                    ? "border-slate-200 bg-white text-slate-700"
                    : "border-amber-200 bg-amber-50 text-amber-950"
              }`}
            >
              {message}
            </div>
          )}

          {/* SUBMIT */}
          <div className="flex flex-col items-start justify-between gap-4 rounded-2xl bg-slate-900 p-6 text-white sm:flex-row sm:items-center sm:p-8">
            <div>
              <h3 className="font-semibold">Ready to plan your room?</h3>
              <p className="mt-1 text-sm text-slate-300">
                Get recommendations tailored to your space and budget.
              </p>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-amber-300 px-6 py-3 font-semibold text-slate-900 transition hover:bg-amber-200 disabled:cursor-not-allowed disabled:opacity-60 sm:w-auto"
            >
              {isLoading ? (
                <LoaderCircle className="animate-spin" size={19} />
              ) : (
                <Sparkles size={19} />
              )}
              {isLoading ? "Analyzing your room..." : "Generate Design"}
            </button>
          </div>
        </form>

        {/* ATTRACTIVE RESULTS DASHBOARD */}
        {result && (
          <section className="mt-12 space-y-8" aria-live="polite">
            {/* REPORT HEADER */}
            <div className="relative overflow-hidden rounded-3xl bg-slate-950 p-6 text-white sm:p-10">
              <div className="absolute -right-16 -top-16 h-56 w-56 rounded-full bg-amber-400/10 blur-3xl" />

              <div className="relative grid gap-8 sm:grid-cols-[1fr_220px] sm:items-center">
                <div>
                  <span className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/10 px-3 py-1.5 text-xs font-medium text-amber-200">
                    <Sparkles size={14} />
                    YOUR PERSONALIZED DESIGN
                  </span>

                  <h2 className="mt-5 text-3xl font-bold tracking-tight sm:text-4xl">
                    Your room, reimagined.
                  </h2>

                  <p className="mt-3 max-w-xl leading-7 text-slate-300">
                    Thoughtful improvements for your space, tailored to your
                    style, existing furniture, and budget.
                  </p>

                  <div className="mt-5 flex flex-wrap gap-2">
                    {[roomType, style, dimensions].filter(Boolean).map((item) => (
                      <span
                        key={item}
                        className="rounded-full bg-white/10 px-3 py-1.5 text-sm text-slate-200"
                      >
                        {item}
                      </span>
                    ))}
                  </div>
                </div>

                {preview && (
                  <img
                    src={preview}
                    alt="Your room"
                    className="h-48 w-full rounded-2xl border border-white/15 object-cover sm:h-52"
                  />
                )}
              </div>
            </div>

            {/* BUDGET */}
            <section>
              <div className="mb-4">
                <h3 className="text-xl font-bold">Your budget at a glance</h3>
                <p className="mt-1 text-sm text-slate-500">
                  A quick overview of your planned spending.
                </p>
              </div>

              <div className="grid gap-4 sm:grid-cols-3">
                <div className="rounded-2xl border border-stone-200 bg-white p-5">
                  <p className="text-sm text-slate-500">Your budget</p>
                  <p className="mt-2 break-words text-2xl font-bold">
                    {formatMoney(budget, currency)}
                  </p>
                </div>

                <div className="rounded-2xl border border-stone-200 bg-white p-5">
                  <p className="text-sm text-slate-500">Estimated product cost</p>
                  <p className="mt-2 break-words text-2xl font-bold">
                    {formatMoney(totalCost, resultCurrency)}
                  </p>
                </div>

                <div className="rounded-2xl border border-stone-200 bg-white p-5">
                  <p className="text-sm text-slate-500">Budget remaining</p>
                  <p className="mt-2 break-words text-2xl font-bold">
                    {formatMoney(remainingBudget, resultCurrency)}
                  </p>
                </div>
              </div>

              {typeof withinBudget === "boolean" && (
                <div
                  className={`mt-4 flex items-start gap-3 rounded-xl border p-4 ${
                    withinBudget
                      ? "border-emerald-200 bg-emerald-50 text-emerald-900"
                      : "border-amber-200 bg-amber-50 text-amber-950"
                  }`}
                >
                  {withinBudget ? (
                    <CheckCircle2 className="mt-0.5 shrink-0" size={20} />
                  ) : (
                    <TriangleAlert className="mt-0.5 shrink-0" size={20} />
                  )}

                  <div>
                    <p className="font-semibold">
                      {withinBudget
                        ? "Your plan fits your budget"
                        : "Your plan exceeds your budget"}
                    </p>
                    <p className="mt-1 text-sm">
                      {withinBudget
                        ? "Your selected products are within your stated budget."
                        : "Consider adjusting the product selection before purchasing."}
                    </p>
                  </div>
                </div>
              )}
            </section>

            {/* DESIGN DIRECTION */}
            {(designOverview || roomIssues || roomOpportunities) && (
              <ResultCard
                title="Your design direction"
                description="The key changes worth focusing on."
                icon={<Lightbulb size={22} />}
              >
                {designOverview && (
                  <p className="leading-7 text-slate-700">{designOverview}</p>
                )}

                <div className="mt-6 grid gap-6 sm:grid-cols-2">
                  {roomIssues && (
                    <div>
                      <h4 className="mb-3 font-semibold">Areas to improve</h4>
                      <ResultList value={roomIssues} />
                    </div>
                  )}

                  {roomOpportunities && (
                    <div>
                      <h4 className="mb-3 font-semibold">
                        Recommended improvements
                      </h4>
                      <ResultList value={roomOpportunities} />
                    </div>
                  )}
                </div>

                {(roomFurniture || roomColors || roomLighting) && (
                  <details className="mt-6 border-t border-stone-200 pt-4">
                    <summary className="cursor-pointer text-sm font-semibold text-slate-700">
                      More about your room analysis
                    </summary>

                    <div className="mt-4 space-y-4 text-sm leading-6 text-slate-600">
                      {roomFurniture && (
                        <p>
                          <span className="font-medium text-slate-900">
                            Furniture:{" "}
                          </span>
                          {displayText(roomFurniture)}
                        </p>
                      )}
                      {roomColors && (
                        <p>
                          <span className="font-medium text-slate-900">
                            Colors:{" "}
                          </span>
                          {displayText(roomColors)}
                        </p>
                      )}
                      {roomLighting && (
                        <p>
                          <span className="font-medium text-slate-900">
                            Lighting:{" "}
                          </span>
                          {displayText(roomLighting)}
                        </p>
                      )}
                    </div>
                  </details>
                )}
              </ResultCard>
            )}

            {/* PRODUCTS */}
            <section>
              <div className="mb-5">
                <h3 className="text-xl font-bold">Recommended for your room</h3>
                <p className="mt-1 text-sm text-slate-500">
                  Items selected for your design plan.
                </p>
              </div>

              {products.length > 0 ? (
                <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
                  {products.map((product, index) => {
                    const name =
                      displayText(
                        getField(product, ["name", "product_name", "title"])
                      ) || "Recommended item";

                    const price = getField(product, [
                      "price",
                      "cost",
                      "estimated_price",
                      "price_pkr",
                      "displayed_price",
                    ]);

                    const reason = displayText(
                      getField(product, [
                        "reason",
                        "description",
                        "benefit",
                        "justification",
                      ])
                    );

                    const category = displayText(
                      getField(product, ["category", "type"])
                    );

                    return (
                      <article
                        key={`${name}-${index}`}
                        className="flex flex-col rounded-2xl border border-stone-200 bg-white p-5 transition hover:-translate-y-1 hover:shadow-lg"
                      >
                        <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-stone-100 text-slate-800">
                          <Package size={24} />
                        </div>

                        {category && (
                          <p className="mt-4 text-xs font-semibold uppercase tracking-wider text-slate-500">
                            {category}
                          </p>
                        )}

                        <h4 className="mt-2 text-lg font-semibold">{name}</h4>

                        {reason && (
                          <p className="mt-2 flex-1 text-sm leading-6 text-slate-600">
                            {reason}
                          </p>
                        )}

                        <div className="mt-5 border-t border-stone-100 pt-4">
                          <p className="text-xs text-slate-500">Estimated price</p>
                          <p className="mt-1 text-xl font-bold">
                            {formatMoney(price, resultCurrency)}
                          </p>
                        </div>
                      </article>
                    );
                  })}
                </div>
              ) : (
                <div className="rounded-2xl border border-stone-200 bg-white p-6 text-sm text-slate-600">
                  No individual product recommendations were returned for
                  this design.
                </div>
              )}
            </section>

            {/* OPTIONAL PRIORITIES */}
            {Array.isArray(priorities) && priorities.length > 0 && (
              <details className="rounded-2xl border border-stone-200 bg-white p-5 sm:p-7">
                <summary className="cursor-pointer font-semibold">
                  View design priorities
                </summary>

                <div className="mt-5 space-y-4">
                  {priorities.map((priority: any, index: number) => (
                    <div key={index} className="rounded-xl bg-stone-50 p-4">
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <p className="font-semibold">
                          {displayText(
                            getField(priority, ["category", "name", "title"])
                          ) || `Priority ${index + 1}`}
                        </p>

                        {getField(priority, ["priority", "level"]) && (
                          <span className="rounded-full bg-amber-100 px-3 py-1 text-xs font-medium text-amber-900">
                            {displayText(
                              getField(priority, ["priority", "level"])
                            )}
                          </span>
                        )}
                      </div>

                      {displayText(
                        getField(priority, ["reason", "description"])
                      ) && (
                        <p className="mt-2 text-sm leading-6 text-slate-600">
                          {displayText(
                            getField(priority, ["reason", "description"])
                          )}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              </details>
            )}

            {/* SUCCESS FOOTER */}
            <div className="rounded-2xl border border-emerald-200 bg-emerald-50 p-5 text-emerald-950">
              <div className="flex items-start gap-3">
                <CheckCircle2 className="mt-0.5 shrink-0" size={22} />
                <div>
                  <h3 className="font-semibold">Your design plan is ready</h3>
                  <p className="mt-1 text-sm leading-6">
                    Review the recommendations and estimated costs before
                    making any purchases. Product prices are estimates from
                    the current design data.
                  </p>
                </div>
              </div>
            </div>
          </section>
        )}
      </section>
    </main>
  );
}
