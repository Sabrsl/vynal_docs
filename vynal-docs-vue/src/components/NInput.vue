<template>
  <div class="n-input"
    :class="[
      size ? `n-input--${size}` : '',
      {
        'n-input--prefix': $slots.prefix || prefixIcon,
        'n-input--suffix': $slots.suffix || suffixIcon,
        'n-input--textarea': type === 'textarea',
        'n-input--readonly': readonly,
        'n-input--transparent': transparent
      }
    ]"
  >
    <label v-if="label" class="n-input__label">{{ label }}</label>
    <div class="n-input__wrapper">
      <span v-if="$slots.prefix || prefixIcon" class="n-input__prefix">
        <slot name="prefix">
          <i :class="prefixIcon"></i>
        </slot>
      </span>
      
      <textarea
        v-if="type === 'textarea'"
        class="n-input__inner"
        :class="{ 'is-invalid': invalid }"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :readonly="readonly"
        :rows="rows"
        :maxlength="maxlength"
        @input="$emit('update:modelValue', $event.target.value)"
        @blur="$emit('blur', $event)"
        @focus="$emit('focus', $event)"
      ></textarea>
      
      <input
        v-else
        :type="type"
        class="n-input__inner"
        :class="{ 'is-invalid': invalid }"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :readonly="readonly"
        :maxlength="maxlength"
        @input="$emit('update:modelValue', $event.target.value)"
        @blur="$emit('blur', $event)"
        @focus="$emit('focus', $event)"
      />
      
      <span v-if="$slots.suffix || suffixIcon" class="n-input__suffix">
        <slot name="suffix">
          <i :class="suffixIcon"></i>
        </slot>
      </span>
    </div>
    <div v-if="error" class="n-input__error">{{ error }}</div>
  </div>
</template>

<script>
export default {
  name: 'NInput',
  props: {
    modelValue: {
      type: [String, Number],
      default: ''
    },
    type: {
      type: String,
      default: 'text'
    },
    label: {
      type: String,
      default: ''
    },
    placeholder: {
      type: String,
      default: ''
    },
    size: {
      type: String,
      default: '',
      validator: value => ['', 'small', 'large'].includes(value)
    },
    disabled: {
      type: Boolean,
      default: false
    },
    readonly: {
      type: Boolean,
      default: false
    },
    transparent: {
      type: Boolean,
      default: false
    },
    invalid: {
      type: Boolean,
      default: false
    },
    error: {
      type: String,
      default: ''
    },
    prefixIcon: {
      type: String,
      default: ''
    },
    suffixIcon: {
      type: String,
      default: ''
    },
    maxlength: {
      type: [String, Number],
      default: undefined
    },
    rows: {
      type: [String, Number],
      default: 3
    }
  },
  emits: ['update:modelValue', 'blur', 'focus']
}
</script>

<style lang="scss">
@import '@/styles/components/input.scss';
</style> 