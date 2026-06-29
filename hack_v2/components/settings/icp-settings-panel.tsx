"use client";

import * as React from "react";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
} from "@/components/ui/sheet";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import {
  Settings2,
  Target,
  Users,
  Trophy,
  UserCheck,
  Plus,
  X,
  Save,
  Loader2,
} from "lucide-react";
import { settingsService, type IcpSettings, type PersonaSettings } from "@/services/settings";

interface IcpSettingsPanelProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function IcpSettingsPanel({ open, onOpenChange }: IcpSettingsPanelProps) {
  const [icp, setIcp] = React.useState<IcpSettings>({
    industry: "Software / AI / SaaS / Tech",
    min_employees: 10,
    max_employees: 0,
    qualification_threshold: 60,
  });
  const [personas, setPersonas] = React.useState<PersonaSettings>({
    default: ["Founder", "VP Sales", "Head of Growth"],
    options: [
      "Founder",
      "VP Sales",
      "Head of Growth",
      "CEO",
      "CTO",
      "VP Engineering",
      "Chief Revenue Officer",
      "SVP Sales",
      "Director of Sales",
    ],
  });
  const [customPersona, setCustomPersona] = React.useState("");
  const [isSaving, setIsSaving] = React.useState(false);
  const [toast, setToast] = React.useState<string | null>(null);

  React.useEffect(() => {
    if (open) {
      settingsService.get().then((res) => {
        setIcp(res.icp);
        setPersonas(res.personas);
      }).catch(() => {});
    }
  }, [open]);

  const handleSaveIcp = async () => {
    setIsSaving(true);
    try {
      await settingsService.updateIcp(icp);
      setToast("ICP settings saved");
    } catch {
      setToast("Failed to save ICP settings");
    } finally {
      setIsSaving(false);
    }
  };

  const handleAddPersona = () => {
    const p = customPersona.trim();
    if (!p || personas.default.includes(p) || personas.options.includes(p)) return;
    setPersonas((prev) => ({
      ...prev,
      default: [...prev.default, p],
      options: [...prev.options, p],
    }));
    setCustomPersona("");
  };

  const handleRemovePersona = (persona: string) => {
    setPersonas((prev) => ({
      ...prev,
      default: prev.default.filter((p) => p !== persona),
      options: prev.options.filter((p) => p !== persona),
    }));
  };

  const handleSavePersonas = async () => {
    setIsSaving(true);
    try {
      await settingsService.updatePersonas(personas);
      setToast("Personas saved");
    } catch {
      setToast("Failed to save personas");
    } finally {
      setIsSaving(false);
    }
  };

  React.useEffect(() => {
    if (toast) {
      const t = setTimeout(() => setToast(null), 2500);
      return () => clearTimeout(t);
    }
  }, [toast]);

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent className="overflow-y-auto sm:max-w-md p-0">
        <div className="h-2 bg-gradient-to-r from-indigo-500 via-purple-500 to-indigo-500" />
        <div className="p-6 space-y-6">
          <SheetHeader className="space-y-2 border-b border-border pb-4">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-border bg-muted/40 text-muted-foreground">
                <Settings2 className="h-5 w-5" />
              </div>
              <div>
                <SheetTitle className="text-lg font-bold">Platform Settings</SheetTitle>
                <SheetDescription className="text-xs">
                  Configure ICP criteria and target personas for prospecting.
                </SheetDescription>
              </div>
            </div>
          </SheetHeader>

          {/* Toast */}
          {toast && (
            <div className="bg-emerald-500/10 border border-emerald-500/20 text-emerald-500 text-xs font-semibold px-3 py-2 rounded-lg">
              {toast}
            </div>
          )}

          {/* ICP Criteria Section */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
              <Target className="h-3.5 w-3.5 text-indigo-500" />
              ICP Criteria
            </h4>
            <Card className="border-border bg-card">
              <CardContent className="p-4 space-y-3">
                <div className="space-y-1">
                  <label className="text-[11px] font-semibold text-muted-foreground">Target Industry</label>
                  <Input
                    value={icp.industry}
                    onChange={(e) => setIcp({ ...icp, industry: e.target.value })}
                    className="h-8 text-xs"
                  />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-1">
                    <label className="text-[11px] font-semibold text-muted-foreground flex items-center gap-1">
                      <Users className="h-3 w-3" /> Min Employees
                    </label>
                    <Input
                      type="number"
                      min={0}
                      value={icp.min_employees}
                      onChange={(e) => setIcp({ ...icp, min_employees: Number(e.target.value) })}
                      className="h-8 text-xs"
                    />
                  </div>
                  <div className="space-y-1">
                    <label className="text-[11px] font-semibold text-muted-foreground flex items-center gap-1">
                      <Users className="h-3 w-3" /> Max Employees
                    </label>
                    <Input
                      type="number"
                      min={0}
                      value={icp.max_employees}
                      onChange={(e) => setIcp({ ...icp, max_employees: Number(e.target.value) })}
                      className="h-8 text-xs"
                      placeholder="0 = no limit"
                    />
                  </div>
                </div>
                <div className="space-y-1">
                  <label className="text-[11px] font-semibold text-muted-foreground flex items-center gap-1">
                    <Trophy className="h-3 w-3" /> Qualification Threshold
                  </label>
                  <Input
                    type="number"
                    min={0}
                    max={100}
                    value={icp.qualification_threshold}
                    onChange={(e) => setIcp({ ...icp, qualification_threshold: Number(e.target.value) })}
                    className="h-8 text-xs"
                  />
                </div>
                <Button
                  onClick={handleSaveIcp}
                  size="sm"
                  className="w-full h-8 gap-1.5 text-xs cursor-pointer"
                  disabled={isSaving}
                >
                  {isSaving ? <Loader2 className="h-3 w-3 animate-spin" /> : <Save className="h-3 w-3" />}
                  Save ICP Criteria
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Target Personas Section */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
              <UserCheck className="h-3.5 w-3.5 text-indigo-500" />
              Target Personas
            </h4>
            <Card className="border-border bg-card">
              <CardContent className="p-4 space-y-3">
                <div className="flex flex-wrap gap-1.5">
                  {personas.default.map((persona) => (
                    <Badge
                      key={persona}
                      variant="outline"
                      className="text-[10px] gap-1 pr-1"
                    >
                      {persona}
                      <button
                        onClick={() => handleRemovePersona(persona)}
                        className="p-0.5 rounded-full hover:bg-muted cursor-pointer"
                      >
                        <X className="h-2.5 w-2.5" />
                      </button>
                    </Badge>
                  ))}
                </div>
                <div className="flex gap-2">
                  <Input
                    value={customPersona}
                    onChange={(e) => setCustomPersona(e.target.value)}
                    placeholder="Add persona (e.g. Head of Sales)"
                    className="h-8 text-xs flex-1"
                    onKeyDown={(e) => { if (e.key === "Enter") handleAddPersona(); }}
                  />
                  <Button
                    onClick={handleAddPersona}
                    variant="outline"
                    size="icon"
                    className="h-8 w-8 shrink-0 cursor-pointer"
                  >
                    <Plus className="h-3.5 w-3.5" />
                  </Button>
                </div>
                <Button
                  onClick={handleSavePersonas}
                  size="sm"
                  className="w-full h-8 gap-1.5 text-xs cursor-pointer"
                  disabled={isSaving}
                >
                  {isSaving ? <Loader2 className="h-3 w-3 animate-spin" /> : <Save className="h-3 w-3" />}
                  Save Personas
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </SheetContent>
    </Sheet>
  );
}
