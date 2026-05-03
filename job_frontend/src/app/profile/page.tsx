"use client";

import { ProtectedRoute } from "@/components/ProtectedRoute";
import { useUser } from "@/hooks/useUser";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

function ProfileContent() {
  const { data: user, isLoading } = useUser();

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-10 w-64" />
        <Skeleton className="h-32 w-full" />
      </div>
    );
  }

  if (!user) {
    return <div>Failed to load profile</div>;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Profile</CardTitle>
        <CardDescription>Your account information</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <label className="text-sm font-medium text-muted-foreground">
            Full Name
          </label>
          <p className="text-lg font-medium">{user.full_name || "Not set"}</p>
        </div>
        <div>
          <label className="text-sm font-medium text-muted-foreground">
            Email
          </label>
          <p className="text-lg font-medium">{user.email}</p>
        </div>
        <div>
          <label className="text-sm font-medium text-muted-foreground">
            Status
          </label>
          <p className="text-lg font-medium">
            {user.is_active ? "Active" : "Inactive"}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}

export default function ProfilePage() {
  return (
    <ProtectedRoute>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-3xl font-bold mb-6">My Profile</h1>
        <ProfileContent />
      </div>
    </ProtectedRoute>
  );
}
