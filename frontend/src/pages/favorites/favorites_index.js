import { Card, Title, Pagination, CardList, Container, Main, CheckboxGroup  } from '../../components'
import styles from './styles.module.css'
import { useRecipes } from '../../utils/index.js'
import { useEffect } from 'react'
import api from '../../api'
import MetaTags from 'react-meta-tags'

const Favorites = ({ updateOrders }) => {
  const {
    recipes,
    setRecipes,
    recipesCount,
    setRecipesCount,
    recipesPage,
    setRecipesPage,
    tagsValue,
    handleTagsChange,
    setTagsValue,
    handleLike,
    handleAddToCart
  } = useRecipes()
  
  const getRecipes = ({ page = 1, tags }) => {
    api
      .getRecipes({ page, is_favorited: Number(true), tags })
      .then(res => {
        const { results, count } = res
        setRecipes(results)
        setRecipesCount(count)
      })
  }

  const handleRemoveFromFavorites = ({ id }) => {
    api.removeFromFavorites({ id })
      .then(_ => {
        setRecipes(recipes.filter(recipe => recipe.id !== id))
        setRecipesCount(count => count - 1)
      })
      .catch(err => {
        const { errors } = err
        if (errors) {
          alert(errors)
        }
      })
  }

  const handleLikeOnFavoritesPage = ({ id, toLike }) => {
    if (toLike) {
      handleLike({ id, toLike })
    } else {
      handleRemoveFromFavorites({ id })
    }
  }

  useEffect(_ => {
    getRecipes({ page: recipesPage, tags: tagsValue })
  }, [recipesPage, tagsValue])

  useEffect(_ => {
    api.getTags()
      .then(tags => {
        setTagsValue(tags.map(tag => ({ ...tag, value: true })))
      })
  }, [])


  return <Main>
    <Container>
      <MetaTags>
        <title>Избранное</title>
        <meta name="description" content="Фудграм - Избранное" />
        <meta property="og:title" content="Избранное" />
      </MetaTags>
      <div className={styles.title}>
        <Title title='Избранное' />
        <CheckboxGroup
          values={tagsValue}
          handleChange={value => {
            setRecipesPage(1)
            handleTagsChange(value)
          }}
        />
      </div>
      {recipes.length > 0 && <CardList>
        {recipes.map(card => <Card
          {...card}
          key={card.id}
          updateOrders={updateOrders}
          handleLike={handleLikeOnFavoritesPage}
          handleAddToCart={handleAddToCart}
        />)}
      </CardList>}
      <Pagination
        count={recipesCount}
        limit={6}
        page={recipesPage}
        onPageChange={page => setRecipesPage(page)}
      />
    </Container>
  </Main>
}

export default Favorites

