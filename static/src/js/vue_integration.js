/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onMounted, onWillUnmount, useRef } from "@odoo/owl";

export class VueDashboardPage extends Component {
    setup() {
        this.vueApp = null;
        this.rootRef = useRef("root");
        
        onMounted(async () => {
            await this.loadVueApp('dashboard');
        });
        
        onWillUnmount(() => {
            this.destroyVueApp();
        });
    }

    async loadVueApp(route = 'dashboard') {
        try {
            await this.waitForVueApp();
            
            const mountElement = this.rootRef.el?.querySelector('#vue-mount-point');
            if (mountElement && window.createVueOdooApp) {
                this.vueApp = window.createVueOdooApp(mountElement, route);
                console.log('✓ Vue Dashboard успешно запущен в Odoo');
            } else {
                throw new Error('Элемент для монтирования Vue не найден');
            }
        } catch (error) {
            console.error('❌ Ошибка загрузки Vue приложения:', error);
            this.showError(error);
        }
    }

    async waitForVueApp() {
        return new Promise((resolve) => {
            const checkVue = () => {
                if (typeof window.createVueOdooApp === 'function') {
                    resolve();
                } else {
                    setTimeout(checkVue, 100);
                }
            };
            checkVue();
        });
    }

    destroyVueApp() {
        if (this.vueApp && typeof this.vueApp.unmount === 'function') {
            try {
                this.vueApp.unmount();
                console.log('✓ Vue приложение успешно размонтировано');
            } catch (error) {
                console.error('❌ Ошибка при размонтировании Vue приложения:', error);
            }
        }
    }

    showError(error) {
        const mountElement = this.rootRef.el?.querySelector('#vue-mount-point');
        if (mountElement) {
            mountElement.innerHTML = `
                <div class="vue-error">
                    <div class="alert alert-danger">
                        <h4><i class="fa fa-exclamation-triangle"></i> Ошибка загрузки Vue приложения</h4>
                        <p>${error.message || error}</p>
                        <small>Проверьте консоль браузера для подробностей</small>
                    </div>
                </div>
            `;
        }
    }

    static template = "com.VueDashboardTemplate";
}

export class VuePlansPage extends Component {
    setup() {
        this.vueApp = null;
        this.rootRef = useRef("root");
        
        onMounted(async () => {
            await this.loadVueApp('plans');
        });
        
        onWillUnmount(() => {
            this.destroyVueApp();
        });
    }

    async loadVueApp(route = 'plans') {
        try {
            await this.waitForVueApp();
            
            const mountElement = this.rootRef.el?.querySelector('#vue-mount-point');
            if (mountElement && window.createVueOdooApp) {
                this.vueApp = window.createVueOdooApp(mountElement, route);
                console.log('✓ Vue Plans успешно запущен в Odoo');
            } else {
                throw new Error('Элемент для монтирования Vue не найден');
            }
        } catch (error) {
            console.error('❌ Ошибка загрузки Vue приложения:', error);
            this.showError(error);
        }
    }

    async waitForVueApp() {
        return new Promise((resolve) => {
            const checkVue = () => {
                if (typeof window.createVueOdooApp === 'function') {
                    resolve();
                } else {
                    setTimeout(checkVue, 100);
                }
            };
            checkVue();
        });
    }

    destroyVueApp() {
        if (this.vueApp && typeof this.vueApp.unmount === 'function') {
            try {
                this.vueApp.unmount();
                console.log('✓ Vue приложение успешно размонтировано');
            } catch (error) {
                console.error('❌ Ошибка при размонтировании Vue приложения:', error);
            }
        }
    }

    showError(error) {
        const mountElement = this.rootRef.el?.querySelector('#vue-mount-point');
        if (mountElement) {
            mountElement.innerHTML = `
                <div class="vue-error">
                    <div class="alert alert-danger">
                        <h4><i class="fa fa-exclamation-triangle"></i> Ошибка загрузки Vue приложения</h4>
                        <p>${error.message || error}</p>
                        <small>Проверьте консоль браузера для подробностей</small>
                    </div>
                </div>
            `;
        }
    }

    static template = "com.VuePlansTemplate";
}

// Регистрируем компоненты в Odoo
registry.category("actions").add("vue.dashboard.page", VueDashboardPage);
registry.category("actions").add("vue.plans.page", VuePlansPage);