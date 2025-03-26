<template>
  <div
    class="n-card"
    :class="[
      {
        'n-card--no-shadow': !shadow,
        'n-card--border': border,
        'n-card--hoverable': hoverable,
        'n-card--compact': compact,
        'n-card--disabled': disabled,
        'n-card--loading': loading
      }
    ]"
  >
    <div v-if="$slots.header || title" class="n-card__header">
      <slot name="header">
        <h3 class="n-card__title">{{ title }}</h3>
        <p v-if="subtitle" class="n-card__subtitle">{{ subtitle }}</p>
      </slot>
    </div>
    <div class="n-card__body">
      <slot></slot>
    </div>
    <div v-if="$slots.footer" class="n-card__footer">
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NCard',
  props: {
    title: {
      type: String,
      default: ''
    },
    subtitle: {
      type: String,
      default: ''
    },
    shadow: {
      type: Boolean,
      default: true
    },
    border: {
      type: Boolean,
      default: false
    },
    hoverable: {
      type: Boolean,
      default: false
    },
    compact: {
      type: Boolean,
      default: false
    },
    disabled: {
      type: Boolean,
      default: false
    },
    loading: {
      type: Boolean,
      default: false
    }
  }
}
</script>

<style lang="scss">
@import '@/styles/components/card.scss';
</style> 