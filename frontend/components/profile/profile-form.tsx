"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { CheckCircle, Mail, Phone, User, Heart, Loader2 } from "lucide-react";
import { api } from "@/lib/api";

interface ProfileData {
  name: string;
  phone: string;
  email: string;
  sex: "male" | "female" | "other";
  gender: string;
  age?: number;
  height_cm?: number;
  weight_kg?: number;
}

export function ProfileForm() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [profileComplete, setProfileComplete] = useState(false);
  const [error, setError] = useState("");

  const [formData, setFormData] = useState<ProfileData>({
    name: "",
    phone: "",
    email: "",
    sex: "male",
    gender: "",
    age: 25,
    height_cm: 170,
    weight_kg: 70,
  });

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      const clientId = localStorage.getItem("clientId");
      if (!clientId) {
        router.push("/login");
        return;
      }

      // GET /profile/{client_id}
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/profile/${clientId}`, {
        headers: {
          "Authorization": `Bearer ${localStorage.getItem("authToken")}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setFormData(data);
        setProfileComplete(data.profile_completed);
        setIsEditing(false);
      }
    } catch (err) {
      console.error("Failed to load profile:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSave = async () => {
    try {
      setIsSaving(true);
      setError("");

      const clientId = localStorage.getItem("clientId");
      if (!clientId) {
        setError("Client ID not found");
        return;
      }

      // PATCH /profile/{client_id}
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/profile/${clientId}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${localStorage.getItem("authToken")}`,
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error("Failed to save profile");
      }

      setProfileComplete(true);
      setIsEditing(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="p-4 md:p-6 space-y-6">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-heading font-bold text-dark">Your Profile</h1>
            <p className="text-dark/60 mt-1 font-body">Complete your profile to get started</p>
          </div>
          {profileComplete && (
            <div className="flex items-center gap-2 text-primary">
              <CheckCircle className="w-6 h-6" />
              <span className="font-semibold">Complete</span>
            </div>
          )}
        </div>
      </motion.div>

      {/* Profile Card */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
        <Card className="p-6 space-y-6">
          {/* Error Message */}
          {error && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-700 font-body">{error}</p>
            </div>
          )}

          {/* Form Fields */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Name */}
            <div className="space-y-2">
              <label className="block text-sm font-semibold text-dark font-body">
                <User className="w-4 h-4 inline mr-2" />
                Full Name
              </label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                disabled={!isEditing}
                className="w-full px-4 py-2 border border-border rounded-lg font-body disabled:bg-dark/5 disabled:text-dark/60 focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="John Doe"
              />
            </div>

            {/* Phone */}
            <div className="space-y-2">
              <label className="block text-sm font-semibold text-dark font-body">
                <Phone className="w-4 h-4 inline mr-2" />
                Phone Number
              </label>
              <input
                type="tel"
                name="phone"
                value={formData.phone}
                onChange={handleInputChange}
                disabled={!isEditing}
                className="w-full px-4 py-2 border border-border rounded-lg font-body disabled:bg-dark/5 disabled:text-dark/60 focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="+91 9876543210"
              />
            </div>

            {/* Email */}
            <div className="space-y-2">
              <label className="block text-sm font-semibold text-dark font-body">
                <Mail className="w-4 h-4 inline mr-2" />
                Email
              </label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                disabled={!isEditing}
                className="w-full px-4 py-2 border border-border rounded-lg font-body disabled:bg-dark/5 disabled:text-dark/60 focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="john@example.com"
              />
            </div>

            {/* Sex */}
            <div className="space-y-2">
              <label className="block text-sm font-semibold text-dark font-body">
                <Heart className="w-4 h-4 inline mr-2" />
                Sex
              </label>
              <select
                name="sex"
                value={formData.sex}
                onChange={handleInputChange}
                disabled={!isEditing}
                className="w-full px-4 py-2 border border-border rounded-lg font-body disabled:bg-dark/5 disabled:text-dark/60 focus:outline-none focus:ring-2 focus:ring-primary"
              >
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="other">Other</option>
              </select>
            </div>

            {/* Gender */}
            <div className="space-y-2">
              <label className="block text-sm font-semibold text-dark font-body">
                Gender Identity
              </label>
              <input
                type="text"
                name="gender"
                value={formData.gender}
                onChange={handleInputChange}
                disabled={!isEditing}
                className="w-full px-4 py-2 border border-border rounded-lg font-body disabled:bg-dark/5 disabled:text-dark/60 focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="e.g., Woman, Man, Non-binary"
              />
            </div>

            {/* Age */}
            <div className="space-y-2">
              <label className="block text-sm font-semibold text-dark font-body">
                Age
              </label>
              <input
                type="number"
                name="age"
                value={formData.age || ""}
                onChange={handleInputChange}
                disabled={!isEditing}
                className="w-full px-4 py-2 border border-border rounded-lg font-body disabled:bg-dark/5 disabled:text-dark/60 focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="25"
              />
            </div>

            {/* Height */}
            <div className="space-y-2">
              <label className="block text-sm font-semibold text-dark font-body">
                Height (cm)
              </label>
              <input
                type="number"
                name="height_cm"
                value={formData.height_cm || ""}
                onChange={handleInputChange}
                disabled={!isEditing}
                className="w-full px-4 py-2 border border-border rounded-lg font-body disabled:bg-dark/5 disabled:text-dark/60 focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="170"
              />
            </div>

            {/* Weight */}
            <div className="space-y-2">
              <label className="block text-sm font-semibold text-dark font-body">
                Weight (kg)
              </label>
              <input
                type="number"
                name="weight_kg"
                value={formData.weight_kg || ""}
                onChange={handleInputChange}
                disabled={!isEditing}
                className="w-full px-4 py-2 border border-border rounded-lg font-body disabled:bg-dark/5 disabled:text-dark/60 focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="70"
              />
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-4 pt-4 border-t border-border">
            {!isEditing ? (
              <Button
                onClick={() => setIsEditing(true)}
                className="bg-primary hover:bg-primary/90"
              >
                Edit Profile
              </Button>
            ) : (
              <>
                <Button
                  onClick={handleSave}
                  disabled={isSaving}
                  className="bg-primary hover:bg-primary/90"
                >
                  {isSaving ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Saving...
                    </>
                  ) : (
                    "Save Changes"
                  )}
                </Button>
                <Button
                  onClick={() => {
                    setIsEditing(false);
                    loadProfile();
                  }}
                  variant="outline"
                  disabled={isSaving}
                >
                  Cancel
                </Button>
              </>
            )}
          </div>
        </Card>
      </motion.div>

      {/* Info Box */}
      {profileComplete && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="p-4 bg-primary/10 border border-primary/20 rounded-lg"
        >
          <p className="text-sm font-body text-dark">
            ✨ Your profile is complete! Head to the <strong>7-Day Challenge</strong> tab to get started.
          </p>
        </motion.div>
      )}
    </div>
  );
}
