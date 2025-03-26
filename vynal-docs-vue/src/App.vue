<template>
  <div class="app">
    <div class="app-header">
      <div class="app-logo">
        <img src="@/assets/logo.svg" alt="Vynal Docs" />
        <span class="app-title">Vynal Docs</span>
      </div>
      <div class="app-search">
        <NInput 
          v-model="searchQuery" 
          placeholder="Rechercher un document..." 
          prefixIcon="icon-search"
          size="small"
        />
      </div>
      <div class="app-actions">
        <NButton type="text" icon="icon-bell">
          <span class="notification-badge"></span>
        </NButton>
        <NButton type="text" icon="icon-settings" />
        <div class="user-menu">
          <img src="@/assets/avatar.svg" alt="User" class="user-avatar" />
          <span class="user-name">John Doe</span>
        </div>
      </div>
    </div>
    
    <div class="app-content">
      <div class="app-sidebar">
        <div class="sidebar-item active">
          <i class="icon-documents"></i>
          <span>Documents</span>
        </div>
        <div class="sidebar-item">
          <i class="icon-templates"></i>
          <span>Modèles</span>
        </div>
        <div class="sidebar-item">
          <i class="icon-categories"></i>
          <span>Catégories</span>
        </div>
        <div class="sidebar-item">
          <i class="icon-users"></i>
          <span>Utilisateurs</span>
        </div>
        <div class="sidebar-item">
          <i class="icon-analytics"></i>
          <span>Statistiques</span>
        </div>
        <div class="sidebar-item">
          <i class="icon-settings"></i>
          <span>Paramètres</span>
        </div>
      </div>
      
      <div class="app-main">
        <div class="page-header">
          <h1>Documents</h1>
          <div class="page-actions">
            <NButton type="primary" icon="icon-plus">Nouveau document</NButton>
          </div>
        </div>
        
        <div class="dashboard-grid">
          <NCard 
            v-for="i in 6" 
            :key="i" 
            title="Documents récents" 
            class="dashboard-card"
            hoverable
          >
            <div class="card-content">
              <p>Contenu du widget {{ i }}</p>
            </div>
            <template #footer>
              <NButton type="text" size="small">Voir plus</NButton>
            </template>
          </NCard>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import NButton from '@/components/NButton.vue'
import NCard from '@/components/NCard.vue'
import NInput from '@/components/NInput.vue'

export default {
  name: 'App',
  components: {
    NButton,
    NCard,
    NInput
  },
  data() {
    return {
      searchQuery: ''
    }
  }
}
</script>

<style lang="scss">
@import '@/styles/base.scss';

.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  
  .app-header {
    height: 60px;
    background-color: white;
    border-bottom: 1px solid $--border-color-base;
    padding: 0 $--spacing-lg;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: $--box-shadow-light;
    
    .app-logo {
      display: flex;
      align-items: center;
      gap: $--spacing-sm;
      
      img {
        height: 28px;
      }
      
      .app-title {
        font-weight: $--font-weight-bold;
        font-size: $--font-size-lg;
        color: $--color-text-dark;
      }
    }
    
    .app-search {
      flex: 0 1 400px;
    }
    
    .app-actions {
      display: flex;
      align-items: center;
      gap: $--spacing-md;
      
      .notification-badge {
        position: absolute;
        top: 8px;
        right: 8px;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: $--color-danger;
      }
      
      .user-menu {
        display: flex;
        align-items: center;
        gap: $--spacing-sm;
        cursor: pointer;
        padding: $--spacing-xs $--spacing-sm;
        border-radius: $--border-radius-base;
        margin-left: $--spacing-sm;
        
        &:hover {
          background-color: $--color-background-medium;
        }
        
        .user-avatar {
          width: 32px;
          height: 32px;
          border-radius: 50%;
          background-color: $--color-background-medium;
        }
        
        .user-name {
          font-weight: $--font-weight-medium;
        }
      }
    }
  }
  
  .app-content {
    display: flex;
    flex: 1;
    
    .app-sidebar {
      width: 220px;
      background-color: white;
      border-right: 1px solid $--border-color-base;
      padding: $--spacing-md 0;
      
      .sidebar-item {
        display: flex;
        align-items: center;
        height: 40px;
        padding: 0 $--spacing-lg;
        cursor: pointer;
        color: $--color-text-light;
        transition: $--transition-base;
        
        i {
          margin-right: $--spacing-sm;
          font-size: $--font-size-lg;
        }
        
        &:hover {
          color: $--color-primary;
          background-color: rgba($--color-primary, 0.05);
        }
        
        &.active {
          color: $--color-primary;
          background-color: rgba($--color-primary, 0.1);
          border-left: 3px solid $--color-primary;
          font-weight: $--font-weight-medium;
        }
      }
    }
    
    .app-main {
      flex: 1;
      padding: $--spacing-lg;
      
      .page-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: $--spacing-xl;
        
        h1 {
          margin: 0;
        }
      }
      
      .dashboard-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
        gap: $--spacing-lg;
        
        .dashboard-card {
          .card-content {
            min-height: 120px;
            display: flex;
            align-items: center;
            justify-content: center;
          }
        }
      }
    }
  }
}
</style> 