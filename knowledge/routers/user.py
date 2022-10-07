from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate

from .. import schemas, models, database

router = APIRouter(
    prefix='/user',
    tags=['Users']
)
get_db = database.get_db


@router.get("/activity_statistics")
def activity_statistics(nbd_filter: str, db: Session = Depends(get_db)):
    if nbd_filter not in ['scopus', 'wos', 'risc']:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'{nbd_filter} is not NBD.')

    sum_documents = db.query(func.sum(models.User.document_count)).filter(
        models.User.scientometric_database == nbd_filter).scalar()
    sum_citations = db.query(func.sum(models.User.citation_count)).filter(
        models.User.scientometric_database == nbd_filter).scalar()
    h_average = db.query(func.avg(models.User.h_index)).filter(
        models.User.scientometric_database == nbd_filter).scalar()
    return {'sum_documents': sum_documents, 'sum_citations': sum_citations, 'h_average': h_average}


@router.post('/', status_code=status.HTTP_201_CREATED)
def create_user(request: schemas.User, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.guid == request.guid).first()
    if user:
        if user.fullname != request.fullname:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f'The user with guid {request.guid} already exists in the system.')
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f'You are already exists in the system.')

    new_user = models.User(**request.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {'new user id': new_user.id}


@router.delete('/{user_guid}/{user_id}')
def destroy(user_id: int, user_guid: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id,
                                        models.User.guid == user_guid).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'User with id {user_id} and guid {user_guid} does not exist.')

    db.delete(user)
    db.commit()
    return {'detail': f'User with user_guid {user_guid} is deleted'}


@router.get('/{user_guid}/{user_id}', response_model=schemas.ShowUser,
            response_model_exclude_none=True)
def get_user(user_id: int, user_guid: str, db: Session = Depends(get_db),
             fields: bool | None = None):
    user = db.query(models.User).filter(models.User.id == user_id,
                                        models.User.guid == user_guid).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'User with id {user_id} and guid {user_guid} does not exist.')
    if not fields:
        user.document_count = None
        user.citation_count = None
    return user


@router.get("/", response_model=Page[schemas.ShowSortUser])
def get_all_users(nbd_filter: str, sort_h: bool | None = None,
                  sort_date: bool | None = None, db: Session = Depends(get_db)):
    if nbd_filter not in ['scopus', 'wos', 'risc']:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'{nbd_filter} is not NBD.')

    if sort_h is not None and sort_date is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'You cannot sort by Hirsch and by date at the same time.')

    users = db.query(models.User).filter(models.User.scientometric_database == nbd_filter)

    if sort_h is True:
        users = users.order_by(models.User.h_index.desc())
    elif sort_h is False:
        users = users.order_by(-models.User.h_index.desc())

    elif sort_date is True:
        users = users.order_by(models.User.created_date.desc())
    elif sort_date is False:
        users = users.order_by(-models.User.created_date.desc())

    return paginate(users)
