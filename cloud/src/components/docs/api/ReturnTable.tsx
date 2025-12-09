import { type TypeInfo, TypeLink } from "./TypeLink";

export type ReturnTypeInfo = {
  name?: string;
  type_info: TypeInfo;
  description?: string;
};

interface ReturnTableProps {
  returnType: ReturnTypeInfo;
}

/**
 * Component to display a function's return type in a table format consistent with other tables
 */
export function ReturnTable({ returnType }: ReturnTableProps) {
  if (!returnType || !returnType.type_info) {
    return null;
  }

  return (
    <div className="api-return-type my-6">
      <h3 className="mb-2 text-lg font-semibold">Returns</h3>
      <div className="overflow-x-auto rounded-md border">
        <table className="w-full border-collapse">
          <thead className="bg-muted">
            <tr>
              {returnType.name && <th className="border-b px-4 py-2 text-left">Name</th>}
              <th className="border-b px-4 py-2 text-left">Type</th>
              <th className="border-b px-4 py-2 text-left">Description</th>
            </tr>
          </thead>
          <tbody>
            <tr className="bg-background">
              {returnType.name && (
                <td className="border-b px-4 py-2 font-mono">{returnType.name}</td>
              )}
              <td className="border-b px-4 py-2">
                <TypeLink type={returnType.type_info} />
              </td>
              <td className="border-b px-4 py-2">{returnType.description || "-"}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
