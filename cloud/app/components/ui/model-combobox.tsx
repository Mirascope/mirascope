import { Button } from "@/app/components/ui/button";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/app/components/ui/command";
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/app/components/ui/form";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/app/components/ui/popover";
import { cn } from "@/app/lib/utils";
import { Check, ChevronsUpDown } from "lucide-react";
import { useEffect, useState } from "react";
import type {
  Control,
  FieldPath,
  FieldValues,
  PathValue,
} from "react-hook-form";

type Option = {
  value: string;
  label: string;
};

type ModelComboboxProps<T extends FieldValues, TName extends FieldPath<T>> = {
  control: Control<T>;
  name: FieldPath<T>;
  label: string;
  options: Option[];
  defaultValue?: PathValue<T, TName>;
  isDisabled?: boolean;
};

export const ModelCombobox = <
  T extends FieldValues,
  TName extends FieldPath<T>,
>({
  control,
  name,
  label,
  options,
  defaultValue,
  isDisabled,
}: ModelComboboxProps<T, TName>) => {
  return (
    <FormField
      control={control}
      name={name}
      defaultValue={defaultValue}
      render={({ field }) => {
        const [open, setOpen] = useState(false);
        const [inputValue, setInputValue] = useState(field.value || "");

        useEffect(() => {
          if (defaultValue && !field.value) {
            field.onChange(defaultValue);
          }
        }, [defaultValue, field]);

        const handleSelect = (value: string) => {
          field.onChange(value);
          setInputValue(value);
          setOpen(false);
        };

        return (
          <FormItem>
            <FormLabel>{label}</FormLabel>
            <FormControl>
              <Popover open={open} onOpenChange={setOpen}>
                <PopoverTrigger asChild>
                  <Button
                    variant="outline"
                    type="button"
                    className="flex w-full items-center justify-between rounded-md border px-3 py-2"
                    disabled={isDisabled}
                    onClick={() => setOpen(!open)}
                  >
                    {field.value
                      ? options.find((opt) => opt.value === field.value)
                          ?.label || field.value
                      : "Select an option"}
                    <ChevronsUpDown className="h-4 w-4" />
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-full p-0">
                  <Command>
                    <CommandInput
                      placeholder="Type or select an option..."
                      value={inputValue}
                      disabled={isDisabled}
                      onValueChange={(value) => {
                        setInputValue(value);
                      }}
                    />
                    <CommandList>
                      <CommandEmpty>No results found.</CommandEmpty>
                      <CommandGroup>
                        {options
                          .filter((option) =>
                            option.label
                              .toLowerCase()
                              .includes(inputValue.toLowerCase()),
                          )
                          .map((option) => (
                            <CommandItem
                              key={option.value}
                              disabled={isDisabled}
                              onSelect={() => handleSelect(option.value)}
                            >
                              <Check
                                className={cn(
                                  "mr-2 h-4 w-4",
                                  field.value === option.value
                                    ? "opacity-100"
                                    : "opacity-0",
                                )}
                              />
                              {option.label}
                            </CommandItem>
                          ))}
                        {inputValue &&
                          !options.some(
                            (opt) =>
                              opt.label.toLowerCase() ===
                              inputValue.toLowerCase(),
                          ) && (
                            <CommandItem
                              onSelect={() => handleSelect(inputValue)}
                            >
                              <Check
                                className={cn(
                                  "mr-2 h-4 w-4",
                                  field.value === inputValue
                                    ? "opacity-100"
                                    : "opacity-0",
                                )}
                              />
                              Add "{inputValue}"
                            </CommandItem>
                          )}
                      </CommandGroup>
                    </CommandList>
                  </Command>
                </PopoverContent>
              </Popover>
            </FormControl>
            <FormMessage />
          </FormItem>
        );
      }}
    />
  );
};
