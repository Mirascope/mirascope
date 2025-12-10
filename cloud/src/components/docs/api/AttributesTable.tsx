import { type TypeInfo, TypeLink } from "./TypeLink";

export type Attribute = {
  name: string;
  type_info: TypeInfo;
  description?: string;
};

interface AttributesTableProps {
  attributes: Attribute[];
}

/**
 * Component to display a table of class attributes
 */
export function AttributesTable({ attributes }: AttributesTableProps) {
  if (!attributes || attributes.length === 0) {
    return null;
  }

  return (
    <div className="api-attributes my-6">
      <h3 className="mb-2 text-lg font-semibold">Attributes</h3>
      <div className="overflow-x-auto rounded-md border">
        <table className="w-full border-collapse">
          <thead className="bg-muted">
            <tr>
              <th className="border-b px-4 py-2 text-left">Name</th>
              <th className="border-b px-4 py-2 text-left">Type</th>
              <th className="border-b px-4 py-2 text-left">Description</th>
            </tr>
          </thead>
          <tbody>
            {attributes.map((attr, index) => (
              <tr key={index} className={index % 2 === 0 ? "bg-background" : "bg-muted/20"}>
                <td className="border-b px-4 py-2 font-mono">{attr.name}</td>
                <td className="border-b px-4 py-2">
                  <TypeLink type={attr.type_info} />
                </td>
                <td className="border-b px-4 py-2">{attr.description || "-"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
