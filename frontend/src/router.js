import { createRouter, createWebHistory } from 'vue-router';
import UserRegister from '@/components/auth/UserRegister.vue';
import UserLogin from '@/components/auth/UserLogin.vue';
import AdminDashboard from '@/components/admin/AdminDashboard.vue';
import store from './store'; 
import SectionList from '@/components/sections/SectionList.vue';
import SectionDetail from '@/components/sections/SectionDetail.vue';
import AddSection from '@/components/sections/AddSection.vue';
import BookList from '@/components/books/BookList.vue';
import AddBook from '@/components/books/AddBook.vue';
import UserLoans from '@/components/loan/UserLoans.vue';
import BookDetails from '@/components/books/BookDetails.vue';
import ActiveLoans from '@/components/admin/ActiveLoans.vue';
import AllLoans from '@/components/admin/AllLoans.vue';
import HomePage from './components/HomePage.vue';
import WelcomePage from '@/components/WelcomePage.vue';
import UserList from '@/components/admin/UserList.vue';
import UserDetail from '@/components/admin/UserDetail.vue';


const routes = [
  {
    path: '/register',
    name: 'UserRegister',
    component: UserRegister
  },
  {
    path: '/login',
    name: 'UserLogin',
    component: UserLogin
  },
  { path: '/admindashboard', component: AdminDashboard, meta: { requiresAdmin: true } },
  { path: '/sections', component: SectionList, meta: { requiresAuth: true } },
  { path: '/section/:id', component: SectionDetail, meta: { requiresAuth: true } },
  { path: '/add-section', component: AddSection, meta: { requiresAdmin: true } },
  { path: '/books', component: BookList, meta: { requiresAuth: true } },
  { path: '/add-book', component: AddBook, meta: { requiresAdmin: true } },
  { path: '/my-loans', component: UserLoans, meta: { requiresAuth: true } },
  { path: '/books/:id', name: 'BookDetails', component: BookDetails, meta: { requiresAuth: true } },
  { path: '/active-loans', name: 'ActiveLoans', component: ActiveLoans, meta: { requiresAdmin: true }},
  { path: '/all-loans', name: 'AllLoans', component: AllLoans, meta: { requiresAdmin: true }},
  { path: '/', name: 'Home', component: HomePage, meta: { requiresAuth: true } },
  { path: '/welcome', name: 'Welcome', component: WelcomePage },
  { path: '/admin/users',component: UserList, eta: { requiresAdmin: true } },
  { path: '/admin/users/:id', component: UserDetail, meta: { requiresAdmin: true }
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

router.beforeEach((to, from, next) => {
  const isAuthenticated = store.getters.isAuthenticated;
  const userRole = store.getters.userRole;

  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!isAuthenticated) {
      next('/welcome');
    } else {
      next();
    }
  } else if (to.matched.some(record => record.meta.requiresAdmin)) {
    if (!isAuthenticated) {
      next('/login');
    } else if (userRole !== 'admin') {
      next('/');
    } else {
      next();
    }
  } else if (isAuthenticated && (to.name === 'UserRegister' || to.name === 'UserLogin')) {
    next('/');
  } else {
    next();
  }
});

export default router;
