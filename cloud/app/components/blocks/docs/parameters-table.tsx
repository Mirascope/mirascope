import { type TypeInfo, TypeLink } from "./type-link";

export type Parameter = {
  name: string;
  type_info: TypeInfo;
  description?: string;
  default?: string;
};

interface ParametersTableProps {
  parameters: Parameter[];
}

/**
 * Component to display a table of parameters with their types
 */
export default function ParametersTable({ parameters }: ParametersTableProps) {
  if (!parameters || parameters.length === 0) {
    return null;
  }

  return (
    <div className="api-parameters my-6">
      <h3 className="mb-2 text-lg font-semibold">Parameters</h3>
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
            {parameters.map((param, index) => (
              <tr
                key={index}
                className={index % 2 === 0 ? "bg-background" : "bg-muted/20"}
              >
                <td className="border-b px-4 py-2 font-mono">
                  {param.name}
                  {param.default && (
                    <span className="text-muted-foreground ml-2">
                      = {param.default}
                    </span>
                  )}
                </td>
                <td className="border-b px-4 py-2">
                  <TypeLink type={param.type_info} />
                </td>
                <td className="border-b px-4 py-2">
                  {param.description || "-"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
