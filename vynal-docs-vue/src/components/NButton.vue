<template>
  <button
    class="n-button"
    :class="[
      type ? `n-button--${type}` : '',
      size ? `n-button--${size}` : '',
      {
        'n-button--outlined': outlined,
        'n-button--round': round,
        'n-button--square': square,
        'n-button--block': block
      }
    ]"
    :disabled="disabled"
    @click="$emit('click', $event)"
  >
    <span v-if="$slots.icon || icon" class="n-icon">
      <slot name="icon">
        <i :class="icon"></i>
      </slot>
    </span>
    <span v-if="$slots.default">
      <slot></slot>
    </span>
    <span v-if="$slots.rightIcon || rightIcon" class="n-icon">
      <slot name="rightIcon">
        <i :class="rightIcon"></i>
      </slot>
    </span>
  </button>
</template>

<script>
export default {
  name: 'NButton',
  props: {
    type: {
      type: String,
      default: 'primary',
      validator: value => ['primary', 'secondary', 'tertiary', 'success', 'warning', 'danger', 'text'].includes(value)
    },
    size: {
      type: String,
      default: '',
      validator: value => ['', 'small', 'large'].includes(value)
    },
    icon: {
      type: String,
      default: ''
    },
    rightIcon: {
      type: String,
      default: ''
    },
    outlined: {
      type: Boolean,
      default: false
    },
    round: {
      type: Boolean,
      default: false
    },
    square: {
      type: Boolean,
      default: false
    },
    block: {
      type: Boolean,
      default: false
    },
    disabled: {
      type: Boolean,
      default: false
    }
  },
  emits: ['click']
}
</script>

<style lang="scss">
@import '@/styles/components/button.scss';
</style> 