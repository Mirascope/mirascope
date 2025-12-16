import * as React from "react";
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
  EmojiPicker,
  EmojiPickerContent,
} from "@/app/components/blocks/emoji-picker";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/app/components/ui/popover";
import { cn } from "@/app/lib/utils";
import { CheckIcon } from "@radix-ui/react-icons";
import type { Emoji } from "frimousse";
import { SmileIcon } from "lucide-react";
import { useState } from "react";

// You can use this generic type to customize the item type
export interface ComboboxItem {
  value: string;
  label: string;
}

interface ComboboxBaseProps {
  items: ComboboxItem[];
  popoverText?: string;
  helperText?: string;
  emptyText?: string;
  disabled?: boolean;
  disableAdd?: boolean;
  customTrigger?: React.ReactNode;
  withEmoji?: boolean; // Flag to enable emoji picker
  onAddItem?: (value: string) => void; // Handler for adding new items
  onEmojiSelect?: (emoji: Emoji) => void; // Handler for emoji selection
  // Add controlled open state props
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
}

interface SingleComboboxProps extends ComboboxBaseProps {
  multiple?: false;
  value: string;
  onChange: (value: string) => void;
}

export interface MultipleComboboxProps extends ComboboxBaseProps {
  multiple: true;
  value: string[];
  onChange: (value: string[]) => void;
}

type ComboboxProps = SingleComboboxProps | MultipleComboboxProps;

export function Combobox({
  items,
  value,
  onChange,
  customTrigger,
  withEmoji = false,
  onEmojiSelect,
  popoverText = "Select item...",
  helperText = "Search item...",
  emptyText = "No item found.",
  disabled = false,
  disableAdd = false,
  multiple = false,
  onAddItem,
  // Add controlled open state props with defaults
  open: controlledOpen,
  onOpenChange,
}: ComboboxProps) {
  const isMultiple = multiple === true;
  const [internalOpen, setInternalOpen] = useState(false);

  // Use controlled state if provided, otherwise use internal state
  const isOpen = controlledOpen ?? internalOpen;
  const setOpen = (value: boolean) => {
    if (onOpenChange) {
      onOpenChange(value);
    } else {
      setInternalOpen(value);
    }
  };

  const [emojiIsOpen, setEmojiIsOpen] = useState(false);

  const [inputValue, setInputValue] = useState("");

  // Ensure value is always an array for multiple select
  const safeValue = isMultiple ? (Array.isArray(value) ? value : []) : value;

  const handleSelect = (currentValue: string) => {
    if (multiple) {
      // Type assertion is safe here because we've ensured multiple is true
      const multipleValue = (value as string[]) || [];
      const newValue = [...multipleValue];

      // Check if the value exists in the items array
      const isExistingValue = items.some((item) => item.value === currentValue);

      // If it's a new item and we have an onAddItem handler
      if (!isExistingValue && onAddItem && !newValue.includes(currentValue)) {
        onAddItem(currentValue);
        return; // Return early as the new item will be added to the list through API
      }

      if (newValue.includes(currentValue)) {
        (onChange as (value: string[]) => void)(
          newValue.filter((v) => v !== currentValue),
        );
      } else {
        (onChange as (value: string[]) => void)([...newValue, currentValue]);
      }
    } else {
      // Type assertion is safe here because we've ensured multiple is false
      (onChange as (value: string) => void)(
        currentValue === (value as string) ? "" : currentValue,
      );
      setOpen(false);
    }
    setInputValue("");
  };

  const getLabel = (val: string) => {
    const item = items.find((item) => item.value === val);
    return item ? item.label : val;
  };

  const getDisplayValue = () => {
    if (
      !value ||
      (isMultiple && (!Array.isArray(value) || value.length === 0))
    ) {
      return popoverText;
    }

    if (isMultiple) {
      const multipleValue = value as string[];

      if (multipleValue.length === 1) {
        return getLabel(multipleValue[0]);
      }

      return `${getLabel(multipleValue[0])} +${multipleValue.length - 1} more`;
    } else {
      return getLabel(value as string);
    }
  };

  // Handle emoji selection by appending it to the current input value
  const handleEmojiSelect = (emojiData: Emoji) => {
    const updatedInput = inputValue + emojiData.emoji;
    setInputValue(updatedInput);

    // Also call the external handler if provided
    if (onEmojiSelect) {
      onEmojiSelect(emojiData);
    }
  };

  return (
    <div className="flex flex-col gap-2">
      <Popover open={disabled ? false : isOpen} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          {customTrigger ?? (
            <Button
              variant="outline"
              role="combobox"
              aria-expanded={isOpen}
              disabled={disabled}
              className={cn(
                "w-full justify-between",
                disabled && "cursor-not-allowed opacity-50",
              )}
            >
              {getDisplayValue()}
            </Button>
          )}
        </PopoverTrigger>
        <PopoverContent
          className="w-(--radix-popover-trigger-width) min-w-[200px] p-0"
          align="start"
          sideOffset={4}
        >
          <Command>
            <CommandInput
              placeholder={helperText}
              value={inputValue}
              onValueChange={setInputValue}
              className="h-9"
              {...(withEmoji && {
                customContent: (
                  <Popover open={emojiIsOpen} onOpenChange={setEmojiIsOpen}>
                    <PopoverTrigger asChild>
                      <SmileIcon className="h-4 w-4 cursor-pointer opacity-70 hover:opacity-100" />
                    </PopoverTrigger>
                    <PopoverContent className="w-fit p-0">
                      <EmojiPicker
                        className="h-[342px]"
                        onEmojiSelect={(emojiData) => {
                          handleEmojiSelect(emojiData);
                          setEmojiIsOpen(false);
                        }}
                      >
                        <EmojiPickerContent />
                      </EmojiPicker>
                    </PopoverContent>
                  </Popover>
                ),
              })}
            />
            <CommandList>
              <CommandEmpty>{emptyText}</CommandEmpty>
              <CommandGroup>
                {/* Always show selected items first */}
                {isMultiple &&
                  safeValue.length > 0 &&
                  items
                    .filter((item) => safeValue.includes(item.value))
                    .map((item) => (
                      <CommandItem
                        key={`selected-${item.value}`}
                        value={item.value}
                        onSelect={handleSelect}
                      >
                        <CheckIcon className="mr-2 h-4 w-4 opacity-100" />
                        {item.label}
                      </CommandItem>
                    ))}

                {/* Show filtered unselected items */}
                {items
                  .filter((item) => {
                    // For multiple, don't show items again that we've already shown above
                    if (isMultiple && safeValue.includes(item.value)) {
                      return false;
                    }
                    // Filter by search input
                    return item.label
                      .toLowerCase()
                      .includes(inputValue.toLowerCase());
                  })
                  .map((item) => (
                    <CommandItem
                      key={item.value}
                      value={item.value}
                      onSelect={handleSelect}
                    >
                      <CheckIcon
                        className={cn(
                          "mr-2 h-4 w-4",
                          isMultiple
                            ? safeValue.includes(item.value)
                              ? "opacity-100"
                              : "opacity-0"
                            : value === item.value
                              ? "opacity-100"
                              : "opacity-0",
                        )}
                      />
                      {item.label}
                    </CommandItem>
                  ))}
                {inputValue &&
                  !disableAdd &&
                  !items.some(
                    (item) =>
                      item.label.toLowerCase() === inputValue.toLowerCase(),
                  ) && (
                    <CommandItem value={inputValue} onSelect={handleSelect}>
                      <CheckIcon
                        className={cn(
                          "mr-2 h-4 w-4",
                          isMultiple
                            ? safeValue.includes(inputValue)
                              ? "opacity-100"
                              : "opacity-0"
                            : value === inputValue
                              ? "opacity-100"
                              : "opacity-0",
                        )}
                      />
                      Add &quot;{inputValue}&quot;
                    </CommandItem>
                  )}
              </CommandGroup>
            </CommandList>
          </Command>
        </PopoverContent>
      </Popover>
    </div>
  );
}
