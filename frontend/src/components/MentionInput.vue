<template>
  <div class="mention-input-wrapper" ref="wrapperRef">
    <div
      ref="editorRef"
      class="mention-editor"
      :class="[inputClass, { 'single-line': !multiline }]"
      contenteditable="true"
      :data-placeholder="placeholder"
      @input="handleInput"
      @keydown="handleKeydown"
      @blur="handleBlur"
      @paste="handlePaste"
    ></div>
    
    <div
      v-if="showMentionMenu"
      class="mention-dropdown"
      :style="dropdownStyle"
      ref="dropdownRef"
    >
      <div v-if="loadingMaterials" class="dropdown-loading">
        <div class="spinner-mini"></div>
        <span>加载中...</span>
      </div>
      
      <div v-else-if="filteredMaterials.length === 0" class="dropdown-empty">
        <span>{{ searchQuery ? '未找到匹配素材' : '暂无素材' }}</span>
      </div>
      
      <div v-else class="dropdown-list">
        <div
          v-for="(material, index) in filteredMaterials"
          :key="material.id"
          class="dropdown-item"
          :class="{ active: index === selectedIndex }"
          @mousedown.prevent="selectMaterial(material)"
          @mouseenter="selectedIndex = index"
        >
          <span class="item-icon">{{ getTypeIcon(material.type) }}</span>
          <div class="item-content">
            <div class="item-name">{{ material.name }}</div>
            <div class="item-preview">{{ getPreviewText(material) }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted } from 'vue'
import materialApi, { type Material } from '../services/materialApi'

interface Props {
  modelValue: string
  placeholder?: string
  multiline?: boolean
  rows?: number
  inputClass?: string
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: '输入 @ 引用素材...',
  multiline: true,
  rows: 3,
  inputClass: ''
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const editorRef = ref<HTMLDivElement>()
const dropdownRef = ref<HTMLDivElement>()
const wrapperRef = ref<HTMLDivElement>()

const showMentionMenu = ref(false)
const searchQuery = ref('')
const selectedIndex = ref(0)
const loadingMaterials = ref(false)
const allMaterials = ref<Material[]>([])
const isComposing = ref(false)
const lastRange = ref<Range | null>(null)

const filteredMaterials = computed(() => {
  if (!searchQuery.value) {
    return allMaterials.value.slice(0, 10)
  }
  
  const query = searchQuery.value.toLowerCase()
  return allMaterials.value
    .filter(m => 
      m.name.toLowerCase().includes(query) ||
      m.tags.some(tag => tag.toLowerCase().includes(query))
    )
    .slice(0, 10)
})

const dropdownStyle = computed(() => {
  if (!editorRef.value) return {}
  const editor = editorRef.value
  const rect = editor.getBoundingClientRect()
  return {
    top: `${rect.height + 4}px`,
    left: '0px',
    minWidth: '300px',
    maxWidth: '500px'
  }
})

function saveSelection() {
  const selection = window.getSelection()
  if (selection && selection.rangeCount > 0) {
    lastRange.value = selection.getRangeAt(0)
  }
}

function restoreSelection() {
  if (lastRange.value) {
    const selection = window.getSelection()
    if (selection) {
      selection.removeAllRanges()
      selection.addRange(lastRange.value)
    }
  }
}

function getTextBeforeCursor(): string {
  const selection = window.getSelection()
  if (!selection || selection.rangeCount === 0) return ''
  const range = selection.getRangeAt(0)
  const preRange = range.cloneRange()
  if (!editorRef.value) return ''
  preRange.selectNodeContents(editorRef.value)
  preRange.setEnd(range.endContainer, range.endOffset)
  return preRange.toString()
}

function getEditorText(): string {
  if (!editorRef.value) return ''
  const result: string[] = []
  
  function traverse(node: Node) {
    if (node.nodeType === Node.TEXT_NODE) {
      result.push(node.textContent || '')
    } else if (node.nodeType === Node.ELEMENT_NODE) {
      const element = node as HTMLElement
      if (element.classList.contains('mention-tag')) {
        const name = element.getAttribute('data-name') || ''
        const id = element.getAttribute('data-id') || ''
        result.push(`@[${name}](${id})`)
      } else if (element.tagName === 'BR') {
        result.push('\n')
      } else {
        element.childNodes.forEach(child => traverse(child))
      }
    }
  }
  
  editorRef.value.childNodes.forEach(node => traverse(node))
  return result.join('')
}

function textToDOM(text: string): DocumentFragment {
  const fragment = document.createDocumentFragment()
  const mentionRegex = /@\[([^\]]+)\]\(([^)]+)\)/g
  let lastIndex = 0
  let match: RegExpExecArray | null
  
  while ((match = mentionRegex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      const textContent = text.substring(lastIndex, match.index)
      addTextToFragment(fragment, textContent)
    }
    const mentionTag = createMentionTag(match[1], match[2])
    fragment.appendChild(mentionTag)
    lastIndex = match.index + match[0].length
  }
  
  if (lastIndex < text.length) {
    const textContent = text.substring(lastIndex)
    addTextToFragment(fragment, textContent)
  }
  
  return fragment
}

function addTextToFragment(fragment: DocumentFragment, text: string) {
  const lines = text.split('\n')
  lines.forEach((line, idx) => {
    if (idx > 0) fragment.appendChild(document.createElement('br'))
    if (line) fragment.appendChild(document.createTextNode(line))
  })
}

function createMentionTag(name: string, id: string): HTMLElement {
  const span = document.createElement('span')
  span.className = 'mention-tag'
  span.contentEditable = 'false'
  span.setAttribute('data-name', name)
  span.setAttribute('data-id', id)
  const material = allMaterials.value.find(m => m.id === id)
  const icon = material ? getTypeIcon(material.type) : '📎'
  span.textContent = `${icon} ${name}`
  return span
}

function insertMentionTag(material: Material) {
  if (!editorRef.value) return
  restoreSelection()
  const selection = window.getSelection()
  if (!selection || selection.rangeCount === 0) return
  const range = selection.getRangeAt(0)
  const textBeforeCursor = getTextBeforeCursor()
  const atIndex = textBeforeCursor.lastIndexOf('@')
  
  if (atIndex !== -1) {
    const deleteCount = textBeforeCursor.length - atIndex
    for (let i = 0; i < deleteCount; i++) {
      if (range.startOffset > 0) {
        range.setStart(range.startContainer, range.startOffset - 1)
        range.deleteContents()
      }
    }
  }
  
  const mentionTag = createMentionTag(material.name, material.id)
  range.insertNode(mentionTag)
  const space = document.createTextNode('\u00A0')
  range.setStartAfter(mentionTag)
  range.insertNode(space)
  range.setStartAfter(space)
  range.collapse(true)
  selection.removeAllRanges()
  selection.addRange(range)
  handleInput()
}

function handleInput() {
  if (isComposing.value) return
  const text = getEditorText()
  emit('update:modelValue', text)
  saveSelection()
  checkForMention()
}

function checkForMention() {
  const textBeforeCursor = getTextBeforeCursor()
  const atIndex = textBeforeCursor.lastIndexOf('@')
  
  if (atIndex !== -1) {
    const searchText = textBeforeCursor.substring(atIndex + 1)
    if (searchText.includes(' ') || searchText.includes('\n')) {
      showMentionMenu.value = false
      return
    }
    searchQuery.value = searchText
    showMentionMenu.value = true
    selectedIndex.value = 0
    if (allMaterials.value.length === 0) {
      loadMaterials()
    }
  } else {
    showMentionMenu.value = false
  }
}

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey && !props.multiline) {
    e.preventDefault()
    return
  }
  
  if (!showMentionMenu.value) return
  
  switch (e.key) {
    case 'ArrowDown':
      e.preventDefault()
      selectedIndex.value = Math.min(selectedIndex.value + 1, filteredMaterials.value.length - 1)
      break
    case 'ArrowUp':
      e.preventDefault()
      selectedIndex.value = Math.max(selectedIndex.value - 1, 0)
      break
    case 'Enter':
      if (filteredMaterials.value.length > 0) {
        e.preventDefault()
        selectMaterial(filteredMaterials.value[selectedIndex.value])
      }
      break
    case 'Escape':
      e.preventDefault()
      showMentionMenu.value = false
      break
  }
}

function selectMaterial(material: Material) {
  insertMentionTag(material)
  showMentionMenu.value = false
  searchQuery.value = ''
  nextTick(() => {
    editorRef.value?.focus()
  })
}

function handleBlur() {
  saveSelection()
  setTimeout(() => {
    showMentionMenu.value = false
  }, 200)
}

function handlePaste(e: ClipboardEvent) {
  e.preventDefault()
  const text = e.clipboardData?.getData('text/plain') || ''
  const selection = window.getSelection()
  if (!selection || selection.rangeCount === 0) return
  const range = selection.getRangeAt(0)
  range.deleteContents()
  const fragment = textToDOM(text)
  range.insertNode(fragment)
  range.collapse(false)
  selection.removeAllRanges()
  selection.addRange(range)
  handleInput()
}

async function loadMaterials() {
  loadingMaterials.value = true
  try {
    const response = await materialApi.getMaterials({ page: 1, page_size: 50 })
    if (response.success && response.data) {
      allMaterials.value = response.data.items
    }
  } catch (error) {
    console.error('加载素材失败:', error)
  } finally {
    loadingMaterials.value = false
  }
}

function getTypeIcon(type: string): string {
  const icons: Record<string, string> = {
    text: '📝', image: '🖼️', reference: '📚'
  }
  return icons[type] || '📄'
}

function getPreviewText(material: Material): string {
  if (material.type === 'text') {
    const text = material.content.text || ''
    return text.length > 40 ? text.substring(0, 40) + '...' : text
  } else if (material.type === 'image') {
    return material.content.description || '图片素材'
  } else if (material.type === 'reference') {
    return material.content.reference_type || '参考素材'
  }
  return material.description || ''
}

watch(() => props.modelValue, (newVal) => {
  if (!editorRef.value) return
  const currentText = getEditorText()
  if (newVal !== currentText) {
    saveSelection()
    editorRef.value.innerHTML = ''
    if (newVal) {
      const fragment = textToDOM(newVal)
      editorRef.value.appendChild(fragment)
    }
  }
})

onMounted(() => {
  loadMaterials()
  if (props.modelValue && editorRef.value) {
    const fragment = textToDOM(props.modelValue)
    editorRef.value.appendChild(fragment)
  }
  editorRef.value?.addEventListener('compositionstart', () => { isComposing.value = true })
  editorRef.value?.addEventListener('compositionend', () => { isComposing.value = false; handleInput() })
})
</script>

<style scoped>
.mention-input-wrapper { position: relative; width: 100%; }
.mention-editor {
  width: 100%; min-height: 80px; padding: 8px 12px; box-sizing: border-box;
  border: 1px solid #d1d5db; border-radius: 6px; font-family: inherit; font-size: 14px;
  line-height: 1.5; color: #111827; background: white; outline: none; overflow-y: auto;
  word-wrap: break-word; white-space: pre-wrap;
}
.mention-editor.single-line { min-height: auto; white-space: nowrap; overflow-x: auto; overflow-y: hidden; }
.mention-editor:focus { border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1); }
.mention-editor:empty:before { content: attr(data-placeholder); color: #9ca3af; pointer-events: none; }
.mention-editor :deep(.mention-tag) {
  display: inline-flex; align-items: center; gap: 4px; padding: 2px 8px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;
  border-radius: 4px; font-size: 13px; font-weight: 500; white-space: nowrap;
  box-shadow: 0 1px 3px rgba(102, 126, 234, 0.3); margin: 0 2px; cursor: default;
}
.mention-dropdown {
  position: absolute; z-index: 1000; background: white; border: 1px solid #e5e7eb;
  border-radius: 8px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); max-height: 300px; overflow-y: auto;
}
.dropdown-loading, .dropdown-empty {
  padding: 16px; text-align: center; color: #6b7280; font-size: 14px;
}
.dropdown-loading { display: flex; align-items: center; justify-content: center; gap: 8px; }
.spinner-mini {
  width: 16px; height: 16px; border: 2px solid #e5e7eb; border-top-color: #3b82f6;
  border-radius: 50%; animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.dropdown-list { padding: 4px; }
.dropdown-item {
  display: flex; align-items: center; gap: 12px; padding: 10px 12px; border-radius: 6px;
  cursor: pointer; transition: background 0.15s;
}
.dropdown-item:hover, .dropdown-item.active { background: #f0f9ff; }
.item-icon { font-size: 20px; flex-shrink: 0; }
.item-content { flex: 1; min-width: 0; }
.item-name { font-size: 14px; font-weight: 500; color: #111827; margin-bottom: 2px; }
.item-preview {
  font-size: 12px; color: #6b7280; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
</style>
