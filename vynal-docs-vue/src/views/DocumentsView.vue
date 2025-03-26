<template>
  <div class="documents-view">
    <div class="page-header">
      <h1>Documents</h1>
      <div class="header-actions">
        <NButton type="text" icon="icon-view-grid" class="view-toggle" />
        <NButton type="text" icon="icon-view-list" class="view-toggle active" />
        <NButton type="outlined" icon="icon-filter">Filtrer</NButton>
        <NButton type="primary" icon="icon-upload">Importer</NButton>
        <NButton type="primary" icon="icon-plus">Nouveau</NButton>
      </div>
    </div>
    
    <div class="documents-filters">
      <div class="filter-group">
        <NInput 
          v-model="search" 
          placeholder="Rechercher..." 
          prefixIcon="icon-search"
          size="small"
        />
      </div>
      <div class="filter-group">
        <label>Trier par:</label>
        <select class="n-input__inner">
          <option>Date (plus récent)</option>
          <option>Date (plus ancien)</option>
          <option>Nom (A-Z)</option>
          <option>Nom (Z-A)</option>
          <option>Taille</option>
        </select>
      </div>
      <div class="filter-group">
        <label>Type:</label>
        <select class="n-input__inner">
          <option>Tous les documents</option>
          <option>PDF</option>
          <option>Word</option>
          <option>Excel</option>
          <option>Images</option>
        </select>
      </div>
    </div>
    
    <NCard class="documents-table-card">
      <table class="documents-table">
        <thead>
          <tr>
            <th class="checkbox-col">
              <input type="checkbox" class="table-checkbox" />
            </th>
            <th>Nom</th>
            <th>Type</th>
            <th>Taille</th>
            <th>Modifié le</th>
            <th>Créé par</th>
            <th class="actions-col">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="i in 10" :key="i">
            <td>
              <input type="checkbox" class="table-checkbox" />
            </td>
            <td class="name-cell">
              <div class="file-icon" :class="`file-icon-${i % 4 === 0 ? 'pdf' : i % 3 === 0 ? 'doc' : i % 2 === 0 ? 'xls' : 'img'}`">
                <i :class="`icon-file-${i % 4 === 0 ? 'pdf' : i % 3 === 0 ? 'doc' : i % 2 === 0 ? 'xls' : 'img'}`"></i>
              </div>
              <span>Document {{ i }}.{{ i % 4 === 0 ? 'pdf' : i % 3 === 0 ? 'docx' : i % 2 === 0 ? 'xlsx' : 'jpg' }}</span>
            </td>
            <td>{{ i % 4 === 0 ? 'PDF' : i % 3 === 0 ? 'Document Word' : i % 2 === 0 ? 'Feuille Excel' : 'Image' }}</td>
            <td>{{ Math.floor(Math.random() * 10) + 1 }}{{ Math.random() > 0.5 ? ' MB' : ' KB' }}</td>
            <td>{{ new Date().toLocaleDateString() }}</td>
            <td>John Doe</td>
            <td class="actions-cell">
              <NButton type="text" icon="icon-view" size="small" title="Voir" />
              <NButton type="text" icon="icon-edit" size="small" title="Modifier" />
              <NButton type="text" icon="icon-share" size="small" title="Partager" />
              <NButton type="text" icon="icon-download" size="small" title="Télécharger" />
              <NButton type="text" icon="icon-trash" size="small" title="Supprimer" class="danger" />
            </td>
          </tr>
        </tbody>
      </table>
      
      <div class="table-pagination">
        <span class="pagination-info">Affichage de 1 à 10 sur 24 documents</span>
        <div class="pagination-controls">
          <NButton type="text" icon="icon-chevron-left" size="small" disabled />
          <span class="pagination-page active">1</span>
          <span class="pagination-page">2</span>
          <span class="pagination-page">3</span>
          <NButton type="text" icon="icon-chevron-right" size="small" />
        </div>
      </div>
    </NCard>
  </div>
</template>

<script>
import NButton from '@/components/NButton.vue'
import NCard from '@/components/NCard.vue'
import NInput from '@/components/NInput.vue'

export default {
  name: 'DocumentsView',
  components: {
    NButton,
    NCard,
    NInput
  },
  data() {
    return {
      search: '',
      documents: []
    }
  }
}
</script>

<style lang="scss">
@import '@/styles/variables.scss';

.documents-view {
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: $--spacing-lg;
    
    h1 {
      margin: 0;
      font-size: $--font-size-3xl;
    }
    
    .header-actions {
      display: flex;
      gap: $--spacing-sm;
      
      .view-toggle {
        padding: $--spacing-xs;
        
        &.active {
          background-color: rgba($--color-primary, 0.1);
          color: $--color-primary;
        }
      }
    }
  }
  
  .documents-filters {
    display: flex;
    align-items: center;
    margin-bottom: $--spacing-lg;
    gap: $--spacing-lg;
    
    .filter-group {
      display: flex;
      align-items: center;
      gap: $--spacing-xs;
      
      label {
        font-size: $--font-size-sm;
        color: $--color-text-light;
        white-space: nowrap;
      }
      
      &:first-child {
        flex: 1;
        max-width: 300px;
      }
      
      select.n-input__inner {
        height: 32px;
        padding: 0 $--spacing-xl 0 $--spacing-sm;
      }
    }
  }
  
  .documents-table-card {
    .documents-table {
      width: 100%;
      border-collapse: collapse;
      
      th, td {
        padding: $--spacing-sm $--spacing-md;
        text-align: left;
        border-bottom: 1px solid $--border-color-lighter;
        
        &:first-child {
          padding-left: $--spacing-lg;
        }
        
        &:last-child {
          padding-right: $--spacing-lg;
        }
      }
      
      th {
        color: $--color-text-light;
        font-weight: $--font-weight-medium;
        font-size: $--font-size-sm;
        background-color: $--color-background-xlight;
      }
      
      .checkbox-col {
        width: 40px;
      }
      
      .actions-col {
        width: 160px;
        text-align: right;
      }
      
      .table-checkbox {
        width: 16px;
        height: 16px;
        border-radius: $--border-radius-base;
        border: 1px solid $--border-color-base;
        appearance: none;
        outline: none;
        cursor: pointer;
        
        &:checked {
          background-color: $--color-primary;
          border-color: $--color-primary;
          position: relative;
          
          &::after {
            content: '';
            position: absolute;
            width: 4px;
            height: 8px;
            border: solid white;
            border-width: 0 2px 2px 0;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -60%) rotate(45deg);
          }
        }
      }
      
      .name-cell {
        display: flex;
        align-items: center;
        gap: $--spacing-sm;
        
        .file-icon {
          width: 32px;
          height: 32px;
          border-radius: $--border-radius-base;
          display: flex;
          align-items: center;
          justify-content: center;
          
          &-pdf {
            background-color: rgba(red, 0.1);
            color: red;
          }
          
          &-doc {
            background-color: rgba(blue, 0.1);
            color: blue;
          }
          
          &-xls {
            background-color: rgba(green, 0.1);
            color: green;
          }
          
          &-img {
            background-color: rgba(purple, 0.1);
            color: purple;
          }
        }
      }
      
      .actions-cell {
        white-space: nowrap;
        text-align: right;
        
        .n-button {
          margin-left: $--spacing-xs;
          opacity: 0.5;
          transition: $--transition-base;
          
          &:hover {
            opacity: 1;
          }
          
          &.danger:hover {
            color: $--color-danger;
          }
        }
      }
      
      tr:hover td {
        background-color: rgba($--color-primary, 0.02);
      }
    }
    
    .table-pagination {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: $--spacing-md $--spacing-lg;
      border-top: 1px solid $--border-color-lighter;
      
      .pagination-info {
        color: $--color-text-light;
        font-size: $--font-size-sm;
      }
      
      .pagination-controls {
        display: flex;
        align-items: center;
        gap: $--spacing-xs;
        
        .pagination-page {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          width: 28px;
          height: 28px;
          border-radius: $--border-radius-base;
          font-size: $--font-size-sm;
          cursor: pointer;
          
          &:hover {
            background-color: $--color-background-medium;
          }
          
          &.active {
            background-color: $--color-primary;
            color: white;
          }
        }
      }
    }
  }
}
</style> 