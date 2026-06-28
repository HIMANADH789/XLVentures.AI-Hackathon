"use client";

import * as React from "react";
import { Building2, Award, Users, Gauge } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Company } from "@/types/company";
import { motion } from "framer-motion";

interface StatsCardsProps {
  companies: Company[];
}

export function StatsCards({ companies }: StatsCardsProps) {
  // Metric calculations
  const totalCompanies = companies.length;
  
  const qualifiedLeads = companies.filter((c) => c.score >= 85).length;
  
  // Dynamic calculation for contacts found, fallback to 0 if not present
  const contactsFound = companies.reduce(
    (acc, curr) => acc + (curr.contacts?.length || 0),
    0
  );
  
  const averageScore =
    totalCompanies > 0
      ? Math.round(companies.reduce((acc, curr) => acc + curr.score, 0) / totalCompanies)
      : 0;

  // Configuration for stats items
  const stats = [
    {
      title: "Total Companies",
      value: totalCompanies,
      icon: Building2,
      description: "Monitored company profiles",
      color: "text-blue-500 bg-blue-500/10 dark:bg-blue-500/20"
    },
    {
      title: "Qualified Leads",
      value: qualifiedLeads,
      icon: Award,
      description: "Leads with score above 85",
      color: "text-emerald-500 bg-emerald-500/10 dark:bg-emerald-500/20"
    },
    {
      title: "Contacts Found",
      value: contactsFound,
      icon: Users,
      description: "Direct decision-makers key info",
      color: "text-indigo-500 bg-indigo-500/10 dark:bg-indigo-500/20"
    },
    {
      title: "Average Score",
      value: `${averageScore}/100`,
      icon: Gauge,
      description: "Mean conversion propensity",
      color: "text-amber-500 bg-amber-500/10 dark:bg-amber-500/20"
    }
  ];

  // Framer Motion container variants
  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.08
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 15 },
    show: { opacity: 1, y: 0, transition: { type: "spring" as const, stiffness: 120, damping: 14 } }
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="show"
      className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4"
    >
      {stats.map((stat, idx) => {
        const IconComponent = stat.icon;
        return (
          <motion.div key={idx} variants={itemVariants}>
            <Card className="hover:shadow-md hover:border-indigo-500/30 dark:hover:border-indigo-500/20 transition-all duration-300 overflow-hidden relative group">
              <div className="absolute inset-0 bg-linear-to-r from-indigo-500/0 via-indigo-500/0 to-indigo-500/0 opacity-0 group-hover:opacity-10 group-hover:from-indigo-500/5 group-hover:to-violet-500/5 transition-all duration-500" />
              <CardContent className="p-6">
                <div className="flex items-center justify-between space-y-0 pb-2">
                  <span className="text-xs font-semibold tracking-wider text-muted-foreground uppercase">
                    {stat.title}
                  </span>
                  <div className={`p-2 rounded-lg ${stat.color}`}>
                    <IconComponent className="h-4.5 w-4.5 stroke-[1.8]" />
                  </div>
                </div>
                <div className="mt-2">
                  <span className="text-2xl font-bold tracking-tight text-foreground">
                    {stat.value}
                  </span>
                  <p className="text-[11px] text-muted-foreground mt-1.5 font-medium">
                    {stat.description}
                  </p>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        );
      })}
    </motion.div>
  );
}
