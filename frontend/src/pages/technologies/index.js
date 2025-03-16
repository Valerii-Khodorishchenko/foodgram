import { Title, Container, Main } from '../../components'
import styles from './styles.module.css'
import MetaTags from 'react-meta-tags'

const Technologies = () => {
  
  return <Main>
    <MetaTags>
      <title>О проекте</title>
      <meta name="description" content="Фудграм - Технологии" />
      <meta property="og:title" content="О проекте" />
    </MetaTags>
    
    <Container>
      <h1 className={styles.title}>Технологии</h1>
      <div className={styles.content}>
        <div>
          <h2 className={styles.subtitle}>Технологии, которые применены в этом проекте:</h2>
          <div className={styles.text}>
            <ul className={styles.textItem}>
              <li className={styles.textItem}>
                Python
              </li>
              <li className={styles.textItem}>
                Бэкенд: Django + Django REST Framework
              </li>
              <li className={styles.textItem}>
                Работа с ползователями: Djoser
              </li>
              <li className={styles.textItem}>
                База данных: PostgreSQL
              </li>
              <li className={styles.textItem}>
                Запуск и проксирование: Gunicorn, Nginx
              </li>
              <li className={styles.textItem}>
                Контейнеризация: Docker, Docker Compose 
              </li>
              <li className={styles.textItem}>
                CI/CD: GitHub Actions (линтинг Flake8, деплой)
              </li>
            </ul>
          </div>
        </div>
      </div>
      
    </Container>
  </Main>
}

export default Technologies

