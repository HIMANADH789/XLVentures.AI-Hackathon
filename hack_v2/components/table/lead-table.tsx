"use client";

import * as React from "react";
import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  SortingState,
  useReactTable
} from "@tanstack/react-table";
import {
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
  ChevronLeft,
  ChevronRight,
  Eye,
  Building2,
  User,
  ExternalLink
} from "lucide-react";
import { Company } from "@/types/company";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

interface LeadTableProps {
  data: Company[];
  onViewCompany: (company: Company) => void;
}

export function LeadTable({ data, onViewCompany }: LeadTableProps) {
  const [sorting, setSorting] = React.useState<SortingState>([]);
  const [pagination, setPagination] = React.useState({
    pageIndex: 0,
    pageSize: 5
  });

  const columns = React.useMemo<ColumnDef<Company>[]>(
    () => [
      {
        accessorKey: "company",
        header: ({ column }) => (
          <button
            onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
            className="flex items-center gap-1.5 hover:text-foreground text-xs font-semibold tracking-wider uppercase select-none cursor-pointer"
          >
            Company
            {column.getIsSorted() === "asc" ? (
              <ArrowUp className="h-3 w-3" />
            ) : column.getIsSorted() === "desc" ? (
              <ArrowDown className="h-3 w-3" />
            ) : (
              <ArrowUpDown className="h-3 w-3 opacity-50" />
            )}
          </button>
        ),
        cell: ({ row }) => {
          const comp = row.original;
          return (
            <div className="flex items-center gap-3">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg border border-border bg-muted/40 text-muted-foreground">
                <Building2 className="h-4 w-4" />
              </div>
              <div className="flex flex-col">
                <span className="font-semibold text-sm text-foreground">
                  {comp.company}
                </span>
                {comp.website ? (
                  <a
                    href={comp.website.startsWith("http") ? comp.website : `https://${comp.website}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-0.5 text-[10px] text-muted-foreground hover:text-indigo-500 hover:underline"
                    onClick={(e) => e.stopPropagation()}
                  >
                    {comp.website.replace("https://", "").replace("http://", "")}
                    <ExternalLink className="h-2.5 w-2.5" />
                  </a>
                ) : (
                  <span className="text-[10px] text-muted-foreground">No URL</span>
                )}
              </div>
            </div>
          );
        }
      },
      {
        accessorKey: "industry",
        header: ({ column }) => (
          <button
            onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
            className="flex items-center gap-1.5 hover:text-foreground text-xs font-semibold tracking-wider uppercase select-none cursor-pointer"
          >
            Industry
            {column.getIsSorted() === "asc" ? (
              <ArrowUp className="h-3 w-3" />
            ) : column.getIsSorted() === "desc" ? (
              <ArrowDown className="h-3 w-3" />
            ) : (
              <ArrowUpDown className="h-3 w-3 opacity-50" />
            )}
          </button>
        ),
        cell: ({ row }) => (
          <span className="text-xs font-medium text-muted-foreground bg-muted/30 border border-border px-2 py-0.5 rounded-md">
            {row.getValue("industry") || "N/A"}
          </span>
        )
      },
      {
        accessorKey: "trigger",
        header: ({ column }) => (
          <button
            onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
            className="flex items-center gap-1.5 hover:text-foreground text-xs font-semibold tracking-wider uppercase select-none cursor-pointer"
          >
            Trigger Event
            {column.getIsSorted() === "asc" ? (
              <ArrowUp className="h-3 w-3" />
            ) : column.getIsSorted() === "desc" ? (
              <ArrowDown className="h-3 w-3" />
            ) : (
              <ArrowUpDown className="h-3 w-3 opacity-50" />
            )}
          </button>
        ),
        cell: ({ row }) => (
          <Badge variant="trigger" className="text-[10px] whitespace-nowrap uppercase">
            {row.getValue("trigger") || "none"}
          </Badge>
        )
      },
      {
        accessorKey: "employees",
        header: ({ column }) => (
          <button
            onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
            className="flex items-center gap-1.5 hover:text-foreground text-xs font-semibold tracking-wider uppercase select-none cursor-pointer"
          >
            Employees
            {column.getIsSorted() === "asc" ? (
              <ArrowUp className="h-3 w-3" />
            ) : column.getIsSorted() === "desc" ? (
              <ArrowDown className="h-3 w-3" />
            ) : (
              <ArrowUpDown className="h-3 w-3 opacity-50" />
            )}
          </button>
        ),
        cell: ({ row }) => {
          const val = row.getValue("employees") as number;
          return (
            <span className="text-xs font-mono font-medium text-foreground">
              {val ? val.toLocaleString() : "N/A"}
            </span>
          );
        }
      },
      {
        accessorKey: "score",
        header: ({ column }) => (
          <button
            onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
            className="flex items-center gap-1.5 hover:text-foreground text-xs font-semibold tracking-wider uppercase select-none cursor-pointer"
          >
            Score
            {column.getIsSorted() === "asc" ? (
              <ArrowUp className="h-3 w-3" />
            ) : column.getIsSorted() === "desc" ? (
              <ArrowDown className="h-3 w-3" />
            ) : (
              <ArrowUpDown className="h-3 w-3 opacity-50" />
            )}
          </button>
        ),
        cell: ({ row }) => {
          const score = row.getValue("score") as number;
          let variant: "success" | "warning" | "danger" = "success";
          if (score >= 85) {
            variant = "success";
          } else if (score >= 70) {
            variant = "warning";
          } else {
            variant = "danger";
          }

          return (
            <Badge variant={variant} className="text-xs font-mono font-bold">
              {score}
            </Badge>
          );
        }
      },
      {
        accessorKey: "contacts",
        header: () => (
          <span className="text-xs font-semibold tracking-wider uppercase text-muted-foreground">
            Primary Contact
          </span>
        ),
        cell: ({ row }) => {
          const contacts = row.original.contacts;
          if (!contacts || contacts.length === 0) {
            return <span className="text-xs text-muted-foreground italic">No contacts</span>;
          }
          const primary = contacts[0];
          return (
            <div className="flex items-center gap-2">
              <div className="flex h-6 w-6 items-center justify-center rounded-full bg-indigo-500/10 text-indigo-500 border border-indigo-500/20">
                <User className="h-3.5 w-3.5" />
              </div>
              <div className="flex flex-col">
                <span className="text-xs font-medium text-foreground leading-normal">
                  {primary.name}
                </span>
                <span className="text-[10px] text-muted-foreground leading-none">
                  {primary.role}
                </span>
              </div>
            </div>
          );
        }
      },
      {
        id: "actions",
        header: () => (
          <span className="text-xs font-semibold tracking-wider uppercase text-muted-foreground text-right block pr-4">
            Actions
          </span>
        ),
        cell: ({ row }) => (
          <div className="flex justify-end pr-2">
            <Button
              variant="outline"
              size="sm"
              onClick={(e) => {
                e.stopPropagation();
                onViewCompany(row.original);
              }}
              className="h-8 gap-1.5 text-xs rounded-lg hover:border-indigo-500/30 hover:bg-indigo-500/5 cursor-pointer"
            >
              <Eye className="h-3.5 w-3.5 text-muted-foreground" />
              <span>View</span>
            </Button>
          </div>
        )
      }
    ],
    [onViewCompany]
  );

  const table = useReactTable({
    data,
    columns,
    state: {
      sorting,
      pagination
    },
    onSortingChange: setSorting,
    onPaginationChange: setPagination,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    pageCount: Math.ceil(data.length / pagination.pageSize)
  });

  return (
    <div className="space-y-4">
      <div className="rounded-xl border border-border bg-card shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              {table.getHeaderGroups().map((headerGroup) => (
                <tr
                  key={headerGroup.id}
                  className="border-b border-border bg-muted/30 h-11"
                >
                  {headerGroup.headers.map((header) => (
                    <th
                      key={header.id}
                      className="px-6 text-xs font-semibold text-muted-foreground align-middle"
                    >
                      {header.isPlaceholder
                        ? null
                        : flexRender(
                            header.column.columnDef.header,
                            header.getContext()
                          )}
                    </th>
                  ))}
                </tr>
              ))}
            </thead>
            <tbody className="divide-y divide-border">
              {table.getRowModel().rows.length > 0 ? (
                table.getRowModel().rows.map((row) => (
                  <tr
                    key={row.id}
                    onClick={() => onViewCompany(row.original)}
                    className="hover:bg-muted/15 transition-colors cursor-pointer h-16 group"
                  >
                    {row.getVisibleCells().map((cell) => (
                      <td
                        key={cell.id}
                        className="px-6 text-sm align-middle whitespace-nowrap"
                      >
                        {flexRender(
                          cell.column.columnDef.cell,
                          cell.getContext()
                        )}
                      </td>
                    ))}
                  </tr>
                ))
              ) : (
                <tr>
                  <td
                    colSpan={columns.length}
                    className="h-24 text-center text-xs text-muted-foreground"
                  >
                    No lead records available.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {data.length > 0 && (
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 py-2 px-1">
          <span className="text-xs text-muted-foreground font-medium">
            Showing{" "}
            <span className="text-foreground font-bold">
              {pagination.pageIndex * pagination.pageSize + 1}
            </span>{" "}
            to{" "}
            <span className="text-foreground font-bold">
              {Math.min(
                (pagination.pageIndex + 1) * pagination.pageSize,
                data.length
              )}
            </span>{" "}
            of <span className="text-foreground font-bold">{data.length}</span>{" "}
            companies
          </span>

          <div className="flex items-center gap-2">
            <span className="text-xs text-muted-foreground mr-2 font-medium">
              Page {table.getState().pagination.pageIndex + 1} of{" "}
              {table.getPageCount() || 1}
            </span>

            <Button
              variant="outline"
              size="icon"
              onClick={() => table.previousPage()}
              disabled={!table.getCanPreviousPage()}
              className="h-8 w-8 rounded-lg cursor-pointer"
              title="Previous Page"
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="icon"
              onClick={() => table.nextPage()}
              disabled={!table.getCanNextPage()}
              className="h-8 w-8 rounded-lg cursor-pointer"
              title="Next Page"
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
