import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/inspiration'
    },
    {
      path: '/result',
      name: 'result',
      component: () => import('../views/ResultView.vue')
    },
    // 板块一：灵感与发现
    {
      path: '/inspiration',
      name: 'inspiration',
      component: () => import('../views/Inspiration/InspirationView.vue')
    },
    {
      path: '/inspiration/trending',
      name: 'inspiration-trending',
      component: () => import('../views/Inspiration/TrendingTopics.vue')
    },
    {
      path: '/inspiration/collector',
      name: 'inspiration-collector',
      component: () => import('../views/Inspiration/ContentCollector.vue')
    },
    {
      path: '/inspiration/templates',
      name: 'inspiration-templates',
      component: () => import('../views/Inspiration/TemplateGallery.vue')
    },
    // 板块二：智能创作
    {
      path: '/creation',
      component: () => import('../views/Creation/CreationView.vue'),
      children: [
        {
          path: '',
          redirect: '/creation/new'
        },
        {
          path: 'new',
          name: 'creation-new',
          component: () => import('../views/Creation/NewCreation.vue')
        },
        {
          path: 'template',
          name: 'creation-template',
          component: () => import('../views/Creation/TemplateCreation.vue')
        }
      ]
    },
    // 板块三：作品与资产
    {
      path: '/workspace',
      component: () => import('../views/Workspace/WorkspaceView.vue'),
      children: [
        {
          path: '',
          redirect: '/workspace/works'
        },
        {
          path: 'works',
          name: 'workspace-works',
          component: () => import('../views/Workspace/Works.vue')
        },
        {
          path: 'assets',
          name: 'workspace-assets',
          component: () => import('../views/Workspace/Assets.vue')
        }
      ]
    },
    // 兼容旧路由的重定向
    {
      path: '/trending',
      redirect: '/inspiration'
    },
    {
      path: '/generator',
      redirect: '/creation/new'
    },
    {
      path: '/history',
      redirect: '/workspace/works'
    },
    {
      path: '/materials',
      redirect: '/workspace/assets'
    },
    {
      path: '/home',
      redirect: '/inspiration/trending'
    }
  ]
})

export default router