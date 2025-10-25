import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from datetime import datetime, timedelta
import numpy as np
from streamlit_option_menu import option_menu
import warnings

# Игнорируем предупреждение о ScriptRunContext
warnings.filterwarnings("ignore", message=".*missing ScriptRunContext.*")

# Настройки страницы
st.set_page_config(
    page_title="MoskSibBusiness Analytics",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

class MoskSibDashboard:
    def __init__(self):
        self.data = {}
        self.selected_period = "Весь период"
        self.load_all_data()
    
    def load_all_data(self):
        """Загружает все JSON файлы с данными"""
        base_path = r"C:\Users\instl\Desktop\Hakaton"
        
        try:
            # Загружаем основные данные
            with open(f"{base_path}/sfera_code_mock_data.json", 'r', encoding='utf-8') as f:
                self.data['sfera'] = json.load(f)
            
            # Загружаем статистику пользователей
            with open(f"{base_path}/user_activity_stats.json", 'r', encoding='utf-8') as f:
                self.data['user_stats'] = json.load(f)
            
            # Загружаем анализ коммитов
            with open(f"{base_path}/commits_analysis_data.json", 'r', encoding='utf-8') as f:
                self.data['commits_analysis'] = json.load(f)
                
            st.sidebar.success("✅ Все данные успешно загружены!")
            
        except FileNotFoundError as e:
            st.error(f"❌ Файл не найден: {e}")
        except json.JSONDecodeError as e:
            st.error(f"❌ Ошибка чтения JSON: {e}")
        except Exception as e:
            st.error(f"❌ Ошибка загрузки данных: {e}")
    
    def filter_data_by_period(self, df, date_column='created_at'):
        """Фильтрует данные по выбранному периоду"""
        if self.selected_period == "Весь период":
            return df
        
        # Определяем дату начала периода
        if self.selected_period == "Последние 30 дней":
            start_date = datetime.now() - timedelta(days=30)
        else:  # "Последние 90 дней"
            start_date = datetime.now() - timedelta(days=90)
        
        # Фильтруем данные
        df[date_column] = pd.to_datetime(df[date_column])
        filtered_df = df[df[date_column] >= start_date]
        
        return filtered_df
    
    def create_sidebar(self):
        """Создает боковую панель"""
        with st.sidebar:
            # Упрощенный заголовок без изображения
            st.markdown("## 🏢 MoskSib Business")
            st.markdown("---")
            
            # Навигация
            selected = option_menu(
                menu_title="Меню",
                options=["📊 Обзор", "👥 Команда", "📈 Активность", "🏆 Рейтинги", "⚙️ Аналитика"],
                icons=["speedometer2", "people", "activity", "trophy", "graph-up"],
                default_index=0,
                styles={
                    "container": {"padding": "5px"},
                    "icon": {"color": "orange", "font-size": "18px"}, 
                    "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px"},
                    "nav-link-selected": {"background-color": "#1E3A8A"},
                }
            )
            
            st.markdown("---")
            st.markdown("### 📅 Период анализа")
            
            # Сохраняем выбранный период
            self.selected_period = st.selectbox(
                "", 
                ["Последние 30 дней", "Последние 90 дней", "Весь период"],
                key="period_selector"
            )
            
            st.info(f"Активный период: {self.selected_period}")
            
            st.markdown("---")
            st.markdown("### 👥 Команда")
            if 'sfera' in self.data:
                st.metric("Разработчиков", len(self.data['sfera'].get('users', [])))
                st.metric("Проектов", len(self.data['sfera'].get('projects', [])))
            
            return selected
    
    def show_overview(self):
        """Главная страница с обзором"""
        st.title("🏢 MoskSib Business Analytics")
        st.markdown("Панель мониторинга эффективности разработки")
        
        # Показываем выбранный период
        st.info(f"📅 Активный период анализа: **{self.selected_period}**")
        
        # Основные метрики
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_commits = self.get_filtered_commits_count()
            st.metric("📝 Коммитов", total_commits)
        
        with col2:
            total_users = self.data.get('user_stats', {}).get('total_users', 0)
            st.metric("👥 Разработчиков", total_users)
        
        with col3:
            total_repos = self.data.get('user_stats', {}).get('total_repositories', 0)
            st.metric("📁 Репозиториев", total_repos)
        
        with col4:
            avg_commits = total_commits / total_users if total_users > 0 else 0
            st.metric("⚡ Активность/чел", f"{avg_commits:.1f}")
        
        st.markdown("---")
        
        # Визуализации
        col1, col2 = st.columns(2)
        
        with col1:
            self.show_commit_timeline()
        
        with col2:
            self.show_user_activity_chart()
    
    def get_filtered_commits_count(self):
        """Возвращает количество коммитов за выбранный период"""
        if 'sfera' not in self.data or 'commits' not in self.data['sfera']:
            return 0
        
        commits = self.data['sfera']['commits']
        df = pd.DataFrame(commits)
        
        if self.selected_period == "Весь период":
            return len(df)
        
        # Фильтруем по периоду
        filtered_df = self.filter_data_by_period(df)
        return len(filtered_df)
    
    def show_commit_timeline(self):
        """График активности коммитов"""
        st.subheader("📈 Активность коммитов")
        
        if 'sfera' not in self.data or 'commits' not in self.data['sfera']:
            st.warning("Нет данных о коммитах")
            return
        
        commits = self.data['sfera']['commits']
        df = pd.DataFrame(commits)
        
        # Применяем фильтрацию
        filtered_df = self.filter_data_by_period(df)
        
        if len(filtered_df) == 0:
            st.warning(f"Нет данных за выбранный период: {self.selected_period}")
            return
        
        filtered_df['created_at'] = pd.to_datetime(filtered_df['created_at'])
        filtered_df['date'] = filtered_df['created_at'].dt.date
        
        # Активность по дням
        daily_activity = filtered_df.groupby('date').size().reset_index(name='commits')
        
        fig = px.line(
            daily_activity, 
            x='date', 
            y='commits',
            title=f"Коммиты по дням ({self.selected_period})",
            labels={'date': 'Дата', 'commits': 'Количество коммитов'}
        )
        fig.update_traces(line=dict(color="#1E3A8A", width=3))
        st.plotly_chart(fig, use_container_width=True)
    
    def show_user_activity_chart(self):
        """График активности пользователей"""
        st.subheader("👥 Активность разработчиков")
        
        if 'user_stats' not in self.data or 'user_activity' not in self.data['user_stats']:
            st.warning("Нет данных о пользователях")
            return
        
        user_activity = self.data['user_stats']['user_activity']
        users_data = []
        
        for email, data in user_activity.items():
            users_data.append({
                'name': data['name'],
                'commits': data['commit_count'],
                'repositories': data['repositories_count']
            })
        
        df = pd.DataFrame(users_data)
        df = df.nlargest(10, 'commits')
        
        fig = px.bar(
            df,
            x='name',
            y='commits',
            title="Топ разработчиков по коммитам",
            labels={'name': 'Разработчик', 'commits': 'Коммиты'},
            color='commits',
            color_continuous_scale='blues'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    def show_team_analytics(self):
        """Аналитика команды"""
        st.title("👥 Аналитика команды")
        
        if 'user_stats' not in self.data:
            st.warning("Нет данных о команде")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Распределение активности")
            user_activity = self.data['user_stats']['user_activity']
            
            names = [data['name'] for data in user_activity.values()]
            commits = [data['commit_count'] for data in user_activity.values()]
            
            fig_pie = px.pie(
                values=commits,
                names=names,
                title="Распределение коммитов между разработчиками"
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            st.subheader("📈 Детальная статистика")
            
            user_activity = self.data['user_stats']['user_activity']
            for email, data in list(user_activity.items())[:5]:
                with st.expander(f"👤 {data['name']}"):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("Коммиты", data['commit_count'])
                    with col_b:
                        st.metric("Репозитории", data['repositories_count'])
                    
                    if 'first_commit' in data and 'last_commit' in data:
                        st.caption(f"Первый коммит: {data['first_commit'][:10]}")
                        st.caption(f"Последний коммит: {data['last_commit'][:10]}")
    
    def show_activity_analytics(self):
        """Детальная аналитика активности"""
        st.title("📈 Детальная аналитика активности")
        st.info(f"📅 Активный период: {self.selected_period}")
        
        if 'sfera' not in self.data:
            return
        
        commits = self.data['sfera']['commits']
        df = pd.DataFrame(commits)
        
        # Применяем фильтрацию
        filtered_df = self.filter_data_by_period(df)
        
        if len(filtered_df) == 0:
            st.warning(f"Нет данных за выбранный период: {self.selected_period}")
            return
        
        filtered_df['created_at'] = pd.to_datetime(filtered_df['created_at'])
        filtered_df['hour'] = filtered_df['created_at'].dt.hour
        filtered_df['day_of_week'] = filtered_df['created_at'].dt.day_name()
        
        tab1, tab2, tab3 = st.tabs(["⏰ По времени суток", "📅 По дням недели", "📋 Детали коммитов"])
        
        with tab1:
            hourly = filtered_df.groupby('hour').size().reset_index(name='count')
            fig_hourly = px.bar(
                hourly,
                x='hour',
                y='count',
                title=f"Активность по времени суток ({self.selected_period})",
                labels={'hour': 'Час дня', 'count': 'Коммиты'}
            )
            st.plotly_chart(fig_hourly, use_container_width=True)
        
        with tab2:
            weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            weekday_data = filtered_df.groupby('day_of_week').size().reindex(weekday_order, fill_value=0).reset_index(name='count')
            
            fig_weekday = px.bar(
                weekday_data,
                x='day_of_week',
                y='count',
                title=f"Активность по дням недели ({self.selected_period})",
                labels={'day_of_week': 'День недели', 'count': 'Коммиты'}
            )
            st.plotly_chart(fig_weekday, use_container_width=True)
        
        with tab3:
            st.subheader(f"Последние коммиты ({self.selected_period})")
            recent_commits = sorted(filtered_df.to_dict('records'), key=lambda x: x['created_at'], reverse=True)[:10]
            
            for commit in recent_commits:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{commit['message']}**")
                    st.caption(f"👤 {commit['author']['name']} | 🕒 {commit['created_at']}")
                with col2:
                    st.code(commit['hash'][:8], language='text')
                st.markdown("---")
    
    def show_rankings(self):
        """Рейтинги и достижения"""
        st.title("🏆 Рейтинги разработчиков")
        
        if 'user_stats' not in self.data:
            return
        
        user_activity = self.data['user_stats']['user_activity']
        ranked_users = sorted(
            [(data['name'], data['commit_count']) for data in user_activity.values()],
            key=lambda x: x[1],
            reverse=True
        )
        
        # Топ-3 разработчика
        col1, col2, col3 = st.columns(3)
        medals = ["🥇", "🥈", "🥉"]
        
        for i, (col, medal) in enumerate(zip([col1, col2, col3], medals)):
            if i < len(ranked_users):
                with col:
                    st.markdown(f"### {medal} {ranked_users[i][0]}")
                    st.metric("Коммиты", ranked_users[i][1])
                    if ranked_users[0][1] > 0:
                        progress = min(ranked_users[i][1] / ranked_users[0][1], 1.0)
                        st.progress(progress)
        
        st.markdown("---")
        
        # Полная таблица рейтингов
        st.subheader("📊 Полный рейтинг команды")
        
        ranking_data = []
        for name, commits in ranked_users:
            ranking_data.append({
                'Разработчик': name,
                'Коммиты': commits,
                'Активность': 'Высокая' if commits > 30 else 'Средняя' if commits > 15 else 'Низкая'
            })
        
        df = pd.DataFrame(ranking_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    def show_advanced_analytics(self):
        """Продвинутая аналитика"""
        st.title("⚙️ Продвинутая аналитика")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Тренды активности")
            if 'sfera' in self.data and 'commits' in self.data['sfera']:
                commits = self.data['sfera']['commits']
                df = pd.DataFrame(commits)
                df = self.filter_data_by_period(df)
                
                if len(df) > 0:
                    df['created_at'] = pd.to_datetime(df['created_at'])
                    df['week'] = df['created_at'].dt.isocalendar().week
                    
                    weekly_trend = df.groupby('week').size().reset_index(name='commits')
                    
                    fig_trend = px.line(
                        weekly_trend,
                        x='week',
                        y='commits',
                        title=f"Тренд активности по неделям ({self.selected_period})",
                        markers=True
                    )
                    st.plotly_chart(fig_trend, use_container_width=True)
                else:
                    st.warning("Нет данных для построения тренда")
        
        with col2:
            st.subheader("💡 Рекомендации")
            
            recommendations = [
                "✅ Отличная активность команды",
                "📊 Рекомендуется увеличить участие в проектах разработчиков с низкой активностью",
                "⏰ Пиковая активность в рабочее время - хорошо",
                "🔄 Рассмотреть ротацию между проектами для обмена опытом"
            ]
            
            for rec in recommendations:
                st.info(rec)
    
    def run(self):
        """Запускает дашборд"""
        if not self.data:
            st.error("Не удалось загрузить данные. Проверьте наличие файлов.")
            return
        
        # Создаем навигацию
        selected_tab = self.create_sidebar()
        
        # Показываем соответствующий раздел
        if selected_tab == "📊 Обзор":
            self.show_overview()
        elif selected_tab == "👥 Команда":
            self.show_team_analytics()
        elif selected_tab == "📈 Активность":
            self.show_activity_analytics()
        elif selected_tab == "🏆 Рейтинги":
            self.show_rankings()
        elif selected_tab == "⚙️ Аналитика":
            self.show_advanced_analytics()
        
        # Футер
        st.markdown("---")
        st.caption(f"© 2025 MoskSib Business | Последнее обновление: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# Запуск дашборда
if __name__ == "__main__":
    dashboard = MoskSibDashboard()
    dashboard.run()
