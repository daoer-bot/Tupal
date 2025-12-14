import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/creation'
    },
    {
      path: '/result',
      name: 'result',
      component: () => import('../views/ResultView.vue'),
      meta: { navKey: 'creation' }
    },
    // 板块一：灵感与发现 (整合版 - 图文采集 + 平台热榜)
    {
      path: '/inspiration',
      name: 'inspiration',
      component: () => import('../views/Inspiration/InspirationView.vue'),
      meta: { navKey: 'inspiration', title: '灵感与发现' }
    },
    // 板块二：AI创作 (整合版)
    {
      path: '/creation',
      component: () => import('../views/Creation/CreationView.vue'),
      meta: { navKey: 'creation' },
      children: [
        {
          path: '',
          name: 'creation-home',
          component: () => import('../views/Creation/CreationHome.vue'),
          meta: { navKey: 'creation', title: 'AI创作' }
        },
        {
          path: 'editor',
          name: 'creation-editor',
          component: () => import('../views/Creation/CreationEditor.vue'),
          meta: { navKey: 'creation', title: '创作编辑器' }
        }
      ]
    },
    // 板块三：资产与作品 (三分版)
    {
      path: '/workspace',
      component: () => import('../views/Workspace/WorkspaceView.vue'),
      meta: { navKey: 'workspace' },
      children: [
        {
          path: '',
          redirect: '/workspace/works'
        },
        {
          path: 'works',
          name: 'works',
          component: () => import('../views/Workspace/WorksTab.vue'),
          meta: { navKey: 'workspace', title: '作品' }
        },
        {
          path: 'knowledge',
          name: 'knowledge',
          component: () => import('../views/Workspace/KnowledgeTab.vue'),
          meta: { navKey: 'workspace', title: '知识' }
        },
        {
          path: 'cases',
          name: 'cases',
          component: () => import('../views/Workspace/CasesTab.vue'),
          meta: { navKey: 'workspace', title: '案例' }
        }
      ]
    }
  ]
})

export default router
