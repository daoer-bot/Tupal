import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/inspiration/trending'
    },
    {
      path: '/result',
      name: 'result',
      component: () => import('../views/ResultView.vue'),
      meta: { navKey: 'creation' }
    },
    // 板块一：灵感与发现 (精简版 - 只保留热榜和采集)
    {
      path: '/inspiration',
      component: () => import('../views/Inspiration/InspirationView.vue'),
      meta: { navKey: 'inspiration' },
      children: [
        {
          path: '',
          redirect: '/inspiration/trending'
        },
        {
          path: 'trending',
          name: 'trending',
          component: () => import('../views/Inspiration/TrendingTopics.vue'),
          meta: { navKey: 'inspiration', title: '平台热榜' }
        },
        {
          path: 'collector',
          name: 'collector',
          component: () => import('../views/Inspiration/ContentCollector.vue'),
          meta: { navKey: 'inspiration', title: '图文采集' }
        }
        // 已移除: InspirationHome.vue (首页入口)
        // 已移除: TemplateGallery.vue (模板广场，将移至AI创作页面)
      ]
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
