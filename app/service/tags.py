from typing import Iterable, List

from sqlalchemy.orm import Session

from app.models.tag import Tag
from app.models.photo import Photo
from app.models.photo_tags import PhotoTag


# move this to .env later?
MAX_TAGS_PER_PHOTO = 5


class TagService:
    @staticmethod
    def attach_tags_to_photo(
        db: Session,
        photo: Photo,
        tag_names: Iterable[str],
    ) -> None:
        """
        Attach tags to photo.
        Creates tags if they do not exist.
        """

        # normalization + uniqueness
        normalized_names = {
            name.strip().lower()
            for name in tag_names
            if name.strip()
        }

        # limitation
        if len(normalized_names) > MAX_TAGS_PER_PHOTO:
            raise ValueError(f"Maximum {MAX_TAGS_PER_PHOTO} tags allowed")

        if not normalized_names:
            return

        # get existing tags with one request
        existing_tags = (
            db.query(Tag)
            .filter(Tag.name.in_(normalized_names))
            .all()
        )

        existing_by_name = {tag.name: tag for tag in existing_tags}

        # making missed tags
        new_tags: List[Tag] = []

        for name in normalized_names:
            if name not in existing_by_name:
                tag = Tag(name=name)
                db.add(tag)
                new_tags.append(tag)

        db.flush()  # new tags get an id

        all_tags = existing_tags + new_tags

        # link to photo no duplicates
        existing_tag_ids = {pt.tag_id for pt in photo.photo_tags}

        for tag in all_tags:
            if tag.id not in existing_tag_ids:
                photo.photo_tags.append(
                    PhotoTag(photo=photo, tag=tag)
                )