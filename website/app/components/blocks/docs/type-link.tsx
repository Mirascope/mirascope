export interface TypeInfo {
  kind: "simple" | "generic" | "union" | "optional" | "callable" | "tuple";
  type_str: string;
  description?: string;
  // Documentation URL for the type (primarily for simple types)
  doc_url?: string;
  // For generic types
  base_type?: TypeInfo;
  parameters?: TypeInfo[];
}

export interface TypeLinkProps {
  type: TypeInfo;
}

/**
 * TypeLink component that displays type information from a structured TypeInfo object.
 * Renders types recursively, with links to documentation where available.
 */
export function TypeLink({ type }: TypeLinkProps) {
  if (!type) {
    return <span className="font-mono">-</span>;
  }

  // For simple types, render with a link if available
  if (type.kind === "simple") {
    const content = <span className="font-mono">{type.type_str}</span>;

    // If we have a documentation URL, make the type clickable
    if (type.doc_url) {
      // Only use rel="noopener noreferrer" for external links
      const isExternal = type.doc_url.startsWith("http");
      return (
        <a
          href={type.doc_url}
          rel={isExternal ? "noopener noreferrer" : undefined}
          className="text-primary font-mono! hover:underline"
        >
          {type.type_str}
        </a>
      );
    }

    return content;
  }

  // For generic types, render recursively
  if (type.kind === "generic" && type.base_type && type.parameters) {
    return (
      <span className="font-mono">
        <TypeLink type={type.base_type} />
        {"["}
        {type.parameters.map((param, index) => (
          <span key={index}>
            {index > 0 && ", "}
            <TypeLink type={param} />
          </span>
        ))}
        {"]"}
      </span>
    );
  }

  // For union types (A | B | C)
  if (type.kind === "union" && type.parameters) {
    return (
      <span className="font-mono">
        {type.parameters.map((param, index) => (
          <span key={index}>
            {index > 0 && " | "}
            <TypeLink type={param} />
          </span>
        ))}
      </span>
    );
  }

  // For optional types (T | None or T?)
  if (
    type.kind === "optional" &&
    type.parameters &&
    type.parameters.length > 0
  ) {
    return (
      <span className="font-mono">
        <TypeLink type={type.parameters[0]} />
        {" | None"}
      </span>
    );
  }

  // For callable types (Callable[[args], return_type])
  if (
    type.kind === "callable" &&
    type.parameters &&
    type.parameters.length === 2
  ) {
    const argsType = type.parameters[0]; // This is usually a tuple
    const returnType = type.parameters[1];

    return (
      <span className="font-mono">
        (
        {argsType.parameters
          ? argsType.parameters.map((param, index) => (
              <span key={index}>
                {index > 0 && ", "}
                <TypeLink type={param} />
              </span>
            ))
          : ""}
        ) {"=> "}
        <TypeLink type={returnType} />
      </span>
    );
  }

  // For tuple types ([A, B, C])
  if (type.kind === "tuple" && type.parameters) {
    return (
      <span className="font-mono">
        {"["}
        {type.parameters.map((param, index) => (
          <span key={index}>
            {index > 0 && ", "}
            <TypeLink type={param} />
          </span>
        ))}
        {"]"}
      </span>
    );
  }

  // For other types or fallback, just render the type string
  return <span className="font-mono">{type.type_str}</span>;
}
