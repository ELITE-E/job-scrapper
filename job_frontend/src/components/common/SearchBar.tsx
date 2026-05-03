"use client";

import React from "react";
import { Input } from "@/components/ui/input";
import { Search } from "lucide-react";

interface SearchBarProps {
	value: string;
	onChange: (value: string) => void;
	placeholder?: string;
	className?: string;
}

export function SearchBar({ value, onChange, placeholder = "Search jobs...", className }: SearchBarProps) {
	return (
		<div className={className}>
			<label htmlFor="search-input" className="sr-only">
				Search
			</label>
			<div className="relative">
				<Search className="absolute left-2 top-1/2 -translate-y-1/2 text-muted-foreground" size={16} aria-hidden />
				<Input
					id="search-input"
					aria-label="Search jobs"
					title="Search jobs"
					value={value}
					onChange={(e) => onChange((e.target as HTMLInputElement).value)}
					placeholder={placeholder}
					className="pl-8"
				/>
			</div>
		</div>
	);
}

export default SearchBar;
