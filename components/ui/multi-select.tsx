import React, { useState } from "react";
import {
  View,
  Text,
  Pressable,
  Modal,
  FlatList,
  StyleSheet,
  Platform,
  TextInput,
} from "react-native";
import MaterialIcons from "@expo/vector-icons/MaterialIcons";
import { useColors } from "@/hooks/use-colors";
import * as Haptics from "expo-haptics";
import { validateBroker } from "@/lib/validators";

export interface MultiSelectOption {
  value: string;
  label: string;
}

interface MultiSelectProps {
  label?: string;
  placeholder?: string;
  options: MultiSelectOption[];
  selectedValues: string[];
  onSelectionChange: (values: string[]) => void;
  error?: string;
  allowCustom?: boolean;
  customValue?: string;
  onCustomValueChange?: (value: string) => void;
  customError?: string;
}

export function MultiSelect({
  label,
  placeholder = "Selecione uma ou mais opções",
  options,
  selectedValues,
  onSelectionChange,
  error,
  allowCustom = false,
  customValue = "",
  onCustomValueChange,
  customError,
}: MultiSelectProps) {
  const colors = useColors();
  const [isOpen, setIsOpen] = useState(false);
  const [localCustomValue, setLocalCustomValue] = useState(customValue);
  const [localCustomError, setLocalCustomError] = useState("");
  const [suggestion, setSuggestion] = useState("");

  const hasOtherSelected = selectedValues.includes("other");

  const selectedLabels = options
    .filter((opt) => selectedValues.includes(opt.value) && opt.value !== "other")
    .map((opt) => opt.label);

  // Add custom broker name if "other" is selected
  if (hasOtherSelected && customValue) {
    selectedLabels.push(customValue);
  }

  const displayText = selectedLabels.length > 0
    ? selectedLabels.length <= 2
      ? selectedLabels.join(", ")
      : `${selectedLabels.slice(0, 2).join(", ")} +${selectedLabels.length - 2}`
    : placeholder;

  const toggleOption = (value: string) => {
    if (Platform.OS !== "web") {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    }
    
    if (selectedValues.includes(value)) {
      onSelectionChange(selectedValues.filter((v) => v !== value));
      // Clear custom value if "other" is deselected
      if (value === "other") {
        setLocalCustomValue("");
        setLocalCustomError("");
        setSuggestion("");
        onCustomValueChange?.("");
      }
    } else {
      onSelectionChange([...selectedValues, value]);
    }
  };

  const handleOpen = () => {
    if (Platform.OS !== "web") {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    }
    setIsOpen(true);
  };

  const handleClose = () => {
    setIsOpen(false);
  };

  const handleCustomValueChange = (value: string) => {
    setLocalCustomValue(value);
    setLocalCustomError("");
    setSuggestion("");
    onCustomValueChange?.(value);
  };

  const handleValidateCustomBroker = () => {
    if (!localCustomValue.trim()) {
      setLocalCustomError("Digite o nome da corretora");
      return;
    }

    const result = validateBroker(localCustomValue);
    if (!result.valid) {
      setLocalCustomError(result.error || "Corretora não encontrada");
      if (result.suggestion) {
        setSuggestion(result.suggestion);
      }
    } else {
      setLocalCustomError("");
      setSuggestion("");
      onCustomValueChange?.(localCustomValue);
    }
  };

  const handleUseSuggestion = () => {
    if (suggestion) {
      const brokerName = suggestion.replace("Você quis dizer: ", "").replace("?", "");
      setLocalCustomValue(brokerName);
      setLocalCustomError("");
      setSuggestion("");
      onCustomValueChange?.(brokerName);
    }
  };

  return (
    <View style={styles.container}>
      {label && (
        <Text style={[styles.label, { color: colors.foreground }]}>{label}</Text>
      )}

      <Pressable
        onPress={handleOpen}
        style={({ pressed }) => [
          styles.selector,
          {
            backgroundColor: colors.surface,
            borderColor: error || customError ? colors.error : colors.border,
          },
          pressed && styles.pressed,
        ]}
      >
        <Text
          style={[
            styles.selectorText,
            {
              color: selectedValues.length > 0 ? colors.foreground : colors.muted,
            },
          ]}
          numberOfLines={1}
        >
          {displayText}
        </Text>
        <MaterialIcons
          name="keyboard-arrow-down"
          size={24}
          color={colors.muted}
        />
      </Pressable>

      {/* Selected chips */}
      {selectedValues.length > 0 && (
        <View style={styles.chipsContainer}>
          {selectedValues.map((value) => {
            if (value === "other") {
              if (!customValue) return null;
              return (
                <Pressable
                  key="custom"
                  onPress={() => toggleOption("other")}
                  style={({ pressed }) => [
                    styles.chip,
                    { backgroundColor: colors.primary + "30" },
                    pressed && styles.pressed,
                  ]}
                >
                  <Text style={[styles.chipText, { color: colors.primary }]}>
                    {customValue}
                  </Text>
                  <MaterialIcons name="close" size={16} color={colors.primary} />
                </Pressable>
              );
            }
            
            const option = options.find((o) => o.value === value);
            if (!option) return null;
            
            return (
              <Pressable
                key={value}
                onPress={() => toggleOption(value)}
                style={({ pressed }) => [
                  styles.chip,
                  { backgroundColor: colors.primary + "30" },
                  pressed && styles.pressed,
                ]}
              >
                <Text style={[styles.chipText, { color: colors.primary }]}>
                  {option.label}
                </Text>
                <MaterialIcons name="close" size={16} color={colors.primary} />
              </Pressable>
            );
          })}
        </View>
      )}

      {/* Custom broker input field (shown when "other" is selected) */}
      {hasOtherSelected && (
        <View style={styles.customInputContainer}>
          <TextInput
            style={[
              styles.customInput,
              {
                backgroundColor: colors.surface,
                borderColor: localCustomError ? colors.error : colors.border,
                color: colors.foreground,
              },
            ]}
            placeholder="Digite o nome da corretora"
            placeholderTextColor={colors.muted}
            value={localCustomValue}
            onChangeText={handleCustomValueChange}
            onBlur={handleValidateCustomBroker}
            autoCapitalize="words"
          />
          {localCustomError && (
            <View style={styles.customErrorContainer}>
              <MaterialIcons name="error-outline" size={14} color={colors.error} />
              <Text style={[styles.customErrorText, { color: colors.error }]}>
                {localCustomError}
              </Text>
            </View>
          )}
          {suggestion && (
            <Pressable
              onPress={handleUseSuggestion}
              style={({ pressed }) => [
                styles.suggestionButton,
                { backgroundColor: colors.primary + "20" },
                pressed && styles.pressed,
              ]}
            >
              <MaterialIcons name="lightbulb" size={16} color={colors.primary} />
              <Text style={[styles.suggestionText, { color: colors.primary }]}>
                {suggestion}
              </Text>
            </Pressable>
          )}
        </View>
      )}

      {error && (
        <Text style={[styles.errorText, { color: colors.error }]}>{error}</Text>
      )}
      {customError && !error && (
        <Text style={[styles.errorText, { color: colors.error }]}>{customError}</Text>
      )}

      {/* Modal for selection */}
      <Modal
        visible={isOpen}
        transparent
        animationType="fade"
        onRequestClose={handleClose}
      >
        <Pressable style={styles.overlay} onPress={handleClose}>
          <View
            style={[
              styles.modalContent,
              { backgroundColor: colors.surface },
            ]}
          >
            <View style={styles.modalHeader}>
              <Text style={[styles.modalTitle, { color: colors.foreground }]}>
                {label || "Selecione"}
              </Text>
              <Pressable onPress={handleClose} style={styles.closeButton}>
                <MaterialIcons name="close" size={24} color={colors.muted} />
              </Pressable>
            </View>

            <Text style={[styles.modalSubtitle, { color: colors.muted }]}>
              Toque para selecionar ou desmarcar
            </Text>

            <FlatList
              data={options}
              keyExtractor={(item) => item.value}
              style={styles.optionsList}
              renderItem={({ item }) => {
                const isSelected = selectedValues.includes(item.value);
                const isOther = item.value === "other";
                
                return (
                  <Pressable
                    onPress={() => toggleOption(item.value)}
                    style={({ pressed }) => [
                      styles.optionItem,
                      {
                        backgroundColor: isSelected
                          ? colors.primary + "20"
                          : "transparent",
                        borderColor: isSelected ? colors.primary : colors.border,
                      },
                      pressed && styles.pressed,
                    ]}
                  >
                    <View
                      style={[
                        styles.checkbox,
                        {
                          backgroundColor: isSelected ? colors.primary : "transparent",
                          borderColor: isSelected ? colors.primary : colors.muted,
                        },
                      ]}
                    >
                      {isSelected && (
                        <MaterialIcons name="check" size={16} color="#0A192F" />
                      )}
                    </View>
                    <View style={styles.optionContent}>
                      <Text
                        style={[
                          styles.optionText,
                          { color: isSelected ? colors.primary : colors.foreground },
                        ]}
                      >
                        {item.label}
                      </Text>
                      {isOther && (
                        <Text style={[styles.optionHint, { color: colors.muted }]}>
                          Digite o nome da corretora
                        </Text>
                      )}
                    </View>
                  </Pressable>
                );
              }}
            />

            <View style={styles.modalFooter}>
              <Pressable
                onPress={handleClose}
                style={({ pressed }) => [
                  styles.confirmButton,
                  { backgroundColor: colors.primary },
                  pressed && styles.pressed,
                ]}
              >
                <Text style={[styles.confirmButtonText, { color: "#0A192F" }]}>
                  Confirmar ({selectedValues.length} selecionado{selectedValues.length !== 1 ? "s" : ""})
                </Text>
              </Pressable>
            </View>
          </View>
        </Pressable>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginBottom: 16,
  },
  label: {
    fontSize: 14,
    fontWeight: "500",
    marginBottom: 8,
  },
  selector: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingHorizontal: 16,
    paddingVertical: 14,
    borderRadius: 12,
    borderWidth: 1,
  },
  pressed: {
    opacity: 0.7,
  },
  selectorText: {
    fontSize: 16,
    flex: 1,
  },
  chipsContainer: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
    marginTop: 12,
  },
  chip: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
    gap: 4,
  },
  chipText: {
    fontSize: 14,
    fontWeight: "500",
  },
  customInputContainer: {
    marginTop: 12,
  },
  customInput: {
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderRadius: 12,
    borderWidth: 1,
    fontSize: 16,
  },
  customErrorContainer: {
    flexDirection: "row",
    alignItems: "center",
    gap: 4,
    marginTop: 6,
  },
  customErrorText: {
    fontSize: 12,
  },
  suggestionButton: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 8,
    marginTop: 8,
  },
  suggestionText: {
    fontSize: 14,
    fontWeight: "500",
  },
  errorText: {
    fontSize: 12,
    marginTop: 4,
  },
  overlay: {
    flex: 1,
    backgroundColor: "rgba(0, 0, 0, 0.7)",
    justifyContent: "center",
    alignItems: "center",
    padding: 24,
  },
  modalContent: {
    width: "100%",
    maxWidth: 400,
    maxHeight: "80%",
    borderRadius: 16,
    overflow: "hidden",
  },
  modalHeader: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: "#1e3a5f",
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: "600",
  },
  closeButton: {
    padding: 4,
  },
  modalSubtitle: {
    fontSize: 14,
    paddingHorizontal: 16,
    paddingVertical: 8,
  },
  optionsList: {
    maxHeight: 300,
  },
  optionItem: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 16,
    paddingVertical: 14,
    borderBottomWidth: 1,
    gap: 12,
  },
  checkbox: {
    width: 24,
    height: 24,
    borderRadius: 6,
    borderWidth: 2,
    alignItems: "center",
    justifyContent: "center",
  },
  optionContent: {
    flex: 1,
  },
  optionText: {
    fontSize: 16,
  },
  optionHint: {
    fontSize: 12,
    marginTop: 2,
  },
  modalFooter: {
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: "#1e3a5f",
  },
  confirmButton: {
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: "center",
  },
  confirmButtonText: {
    fontSize: 16,
    fontWeight: "600",
  },
});
