"""
Management command to seed celebrity data into the database.
Downloads publicly available face images for face matching.

NOTE: Due to Wikimedia's strict robot policies, automated downloads from
upload.wikimedia.org are heavily rate-limited. This command includes
rate limiting and retries, but may still fail.

For reliable seeding, consider:
1. Using a different image source with proper licensing
2. Manually downloading images and placing them in media/celebrities/
3. Using placeholder images for development/testing
"""
import os
import time
import urllib.request
from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings
from matcher.models import Celebrity


# Celebrity data with publicly available image URLs
CELEBRITIES = [
    {
        "name": "Robert Downey Jr.",
        "category": "actor",
        "description": "American actor known for Iron Man and Sherlock Holmes",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/Robert_Downey_Jr_2014_Comic_Con_%28cropped%29.jpg/250px-Robert_Downey_Jr_2014_Comic_Con_%28cropped%29.jpg"
    },
    {
        "name": "Scarlett Johansson",
        "category": "actress",
        "description": "American actress known for Black Widow and Lost in Translation",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/60/Scarlett_Johansson_by_Gage_Skidmore_2_%28cropped%29.jpg/250px-Scarlett_Johansson_by_Gage_Skidmore_2_%28cropped%29.jpg"
    },
    {
        "name": "Chris Hemsworth",
        "category": "actor",
        "description": "Australian actor known for Thor in the Marvel Universe",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e8/Chris_Hemsworth_by_Gage_Skidmore_2_%28cropped%29.jpg/250px-Chris_Hemsworth_by_Gage_Skidmore_2_%28cropped%29.jpg"
    },
    {
        "name": "Taylor Swift",
        "category": "singer",
        "description": "American singer-songwriter and global pop icon",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d7/Taylor_Swift_at_the_2023_MTV_Video_Music_Awards_4.png/250px-Taylor_Swift_at_the_2023_MTV_Video_Music_Awards_4.png"
    },
    {
        "name": "Dwayne Johnson",
        "category": "actor",
        "description": "American actor and former wrestler known as The Rock",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1f/Dwayne_Johnson_2014_%28cropped%29.jpg/250px-Dwayne_Johnson_2014_%28cropped%29.jpg"
    },
    {
        "name": "Emma Watson",
        "category": "actress",
        "description": "British actress known for Hermione in Harry Potter",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7f/Emma_Watson_2013.jpg/250px-Emma_Watson_2013.jpg"
    },
    {
        "name": "Leonardo DiCaprio",
        "category": "actor",
        "description": "American actor known for Titanic and The Revenant",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Leonardo_Dicaprio_Cannes_2019.jpg/250px-Leonardo_Dicaprio_Cannes_2019.jpg"
    },
    {
        "name": "Beyoncé",
        "category": "singer",
        "description": "American singer, songwriter, and cultural icon",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/17/Beyonc%C3%A9_at_The_Lion_King_European_Premiere_2019.png/250px-Beyonc%C3%A9_at_The_Lion_King_European_Premiere_2019.png"
    },
    {
        "name": "Tom Holland",
        "category": "actor",
        "description": "British actor known for Spider-Man in the MCU",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3c/Tom_Holland_by_Gage_Skidmore.jpg/250px-Tom_Holland_by_Gage_Skidmore.jpg"
    },
    {
        "name": "Zendaya",
        "category": "actress",
        "description": "American actress and singer known for Euphoria and Dune",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/28/Zendaya_-_2019_by_Glenn_Francis.jpg/250px-Zendaya_-_2019_by_Glenn_Francis.jpg"
    },
    {
        "name": "Brad Pitt",
        "category": "actor",
        "description": "American actor and producer known for Fight Club and Troy",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Brad_Pitt_2019_by_Glenn_Francis.jpg/250px-Brad_Pitt_2019_by_Glenn_Francis.jpg"
    },
    {
        "name": "Angelina Jolie",
        "category": "actress",
        "description": "American actress and humanitarian known for Tomb Raider",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ad/Angelina_Jolie_2_June_2014_%28cropped%29.jpg/250px-Angelina_Jolie_2_June_2014_%28cropped%29.jpg"
    },
    {
        "name": "Chris Evans",
        "category": "actor",
        "description": "American actor known for Captain America in the MCU",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/ChrisEvans2023.jpg/250px-ChrisEvans2023.jpg"
    },
    {
        "name": "Gal Gadot",
        "category": "actress",
        "description": "Israeli actress known for Wonder Woman",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/Gal_Gadot_2018.jpg/250px-Gal_Gadot_2018.jpg"
    },
    {
        "name": "Cristiano Ronaldo",
        "category": "sports",
        "description": "Portuguese footballer and global sports icon",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8c/Cristiano_Ronaldo_2018.jpg/250px-Cristiano_Ronaldo_2018.jpg"
    },
    {
        "name": "Lionel Messi",
        "category": "sports",
        "description": "Argentine footballer and World Cup champion",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b4/Lionel-Messi-Argentina-2022-FIFA-World-Cup_%28cropped%29.jpg/250px-Lionel-Messi-Argentina-2022-FIFA-World-Cup_%28cropped%29.jpg"
    },
    {
        "name": "Selena Gomez",
        "category": "singer",
        "description": "American singer and actress known for her pop music and acting",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0a/Selena_Gomez_-_2019_by_Glenn_Francis.jpg/250px-Selena_Gomez_-_2019_by_Glenn_Francis.jpg"
    },
    {
        "name": "Keanu Reeves",
        "category": "actor",
        "description": "Canadian actor known for The Matrix and John Wick",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f2/Keanu_Reeves_2023.jpg/250px-Keanu_Reeves_2023.jpg"
    },
    {
        "name": "Margot Robbie",
        "category": "actress",
        "description": "Australian actress known for Barbie and The Wolf of Wall Street",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/14/Margot_Robbie_Cannes_2019.jpg/250px-Margot_Robbie_Cannes_2019.jpg"
    },
    {
        "name": "Shah Rukh Khan",
        "category": "actor",
        "description": "Indian actor known as King Khan of Bollywood",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/Shah_Rukh_Khan_grance_the_launch_of_Seem_%28cropped%29.jpg/250px-Shah_Rukh_Khan_grance_the_launch_of_Seem_%28cropped%29.jpg"
    },
    {
        "name": "Priyanka Chopra",
        "category": "actress",
        "description": "Indian actress and former Miss World",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6a/Priyanka_Chopra_at_Beautycon_2019.jpg/250px-Priyanka_Chopra_at_Beautycon_2019.jpg"
    },
    {
        "name": "Virat Kohli",
        "category": "sports",
        "description": "Indian cricketer and one of the greatest batsmen",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ef/Virat_Kohli_during_the_India_vs_Aus_4th_Test_match_at_Narendra_Modi_Stadium_on_09_March_2023.jpg/250px-Virat_Kohli_during_the_India_vs_Aus_4th_Test_match_at_Narendra_Modi_Stadium_on_09_March_2023.jpg"
    },
    {
        "name": "MS Dhoni",
        "category": "sports",
        "description": "Indian cricket legend and former captain",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f1/Dhoni_at_Chenai.jpg/250px-Dhoni_at_Chenai.jpg"
    },
    {
        "name": "Deepika Padukone",
        "category": "actress",
        "description": "Indian actress and one of Bollywood's top stars",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/43/Deepika_Padukone_Cannes_2022.jpg/250px-Deepika_Padukone_Cannes_2022.jpg"
    },
    {
        "name": "Vijay Thalapathy",
        "category": "actor",
        "description": "Indian Tamil actor and one of the biggest stars of South Indian cinema",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/Vijay_at_the_62nd_Filmfare_Awards_South_%28cropped%29.jpg/250px-Vijay_at_the_62nd_Filmfare_Awards_South_%28cropped%29.jpg"
    },
    {
        "name": "Rajinikanth",
        "category": "actor",
        "description": "Indian actor known as the Superstar of Indian cinema",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/80/Rajinikanth_2012_%28cropped%29.jpg/250px-Rajinikanth_2012_%28cropped%29.jpg"
    },
    {
        "name": "Ariana Grande",
        "category": "singer",
        "description": "American singer and actress with powerful vocals",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d1/Ariana_Grande_Grammys_Red_Carpet_2020.png/250px-Ariana_Grande_Grammys_Red_Carpet_2020.png"
    },
    {
        "name": "Tom Cruise",
        "category": "actor",
        "description": "American actor known for Mission Impossible and Top Gun",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/Tom_Cruise_by_Gage_Skidmore_2.jpg/250px-Tom_Cruise_by_Gage_Skidmore_2.jpg"
    },
    {
        "name": "Ed Sheeran",
        "category": "singer",
        "description": "British singer-songwriter known for Shape of You",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c1/Ed_Sheeran-6886_%28cropped%29.jpg/250px-Ed_Sheeran-6886_%28cropped%29.jpg"
    },
    {
        "name": "Billie Eilish",
        "category": "singer",
        "description": "American singer-songwriter and Gen-Z music icon",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Billie_Eilish_2019_by_Glenn_Francis_%28cropped%29_2.jpg/250px-Billie_Eilish_2019_by_Glenn_Francis_%28cropped%29_2.jpg"
    },
]


class Command(BaseCommand):
    help = 'Seed celebrity data with face images for look-alike matching'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing celebrity data before seeding',
        )
        parser.add_argument(
            '--use-placeholders',
            action='store_true',
            help='Use placeholder images instead of downloading from Wikimedia',
        )
        parser.add_argument(
            '--manual-images',
            action='store_true',
            help='Skip downloads and expect images to be manually placed in media/celebrities/',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING(
            "WARNING: Wikimedia has strict rate limits for automated downloads.\n"
            "This command may fail. Consider using --use-placeholders for testing\n"
            "or --manual-images if you've placed images manually."
        ))

        if options['clear']:
            self.stdout.write("Clearing existing celebrity data...")
            Celebrity.objects.all().delete()

        celeb_dir = os.path.join(settings.MEDIA_ROOT, 'celebrities')
        os.makedirs(celeb_dir, exist_ok=True)

        if options['use_placeholders']:
            return self._seed_with_placeholders(celeb_dir)
        elif options['manual_images']:
            return self._seed_with_manual_images(celeb_dir)
        else:
            return self._seed_with_downloads(celeb_dir)

        success_count = 0
        skip_count = 0
        fail_count = 0

        for i, celeb_data in enumerate(CELEBRITIES):
            name = celeb_data['name']

            # Skip if already exists
            if Celebrity.objects.filter(name=name).exists():
                self.stdout.write(f"  ⏭ Skipping {name} (already exists)")
                skip_count += 1
                continue

            # Download image with retry logic
            safe_name = name.lower().replace(' ', '_').replace('.', '').replace("'", '')
            image_filename = f"{safe_name}.jpg"
            image_path = os.path.join(celeb_dir, image_filename)

            max_retries = 3
            retry_delay = 2  # seconds

            for attempt in range(max_retries):
                try:
                    self.stdout.write(f"  ⬇ Downloading {name}... (attempt {attempt + 1}/{max_retries})")
                    req = urllib.request.Request(
                        celeb_data['image_url'],
                        headers={
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                                          'Chrome/120.0.0.0 Safari/537.36',
                            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                            'Accept-Language': 'en-US,en;q=0.9',
                            'Accept-Encoding': 'gzip, deflate, br',
                            'DNT': '1',
                            'Connection': 'keep-alive',
                            'Upgrade-Insecure-Requests': '1',
                        }
                    )
                    with urllib.request.urlopen(req, timeout=30) as response:
                        with open(image_path, 'wb') as out_file:
                            out_file.write(response.read())

                    # Create celebrity record
                    celeb = Celebrity(
                        name=name,
                        category=celeb_data['category'],
                        description=celeb_data['description'],
                    )
                    with open(image_path, 'rb') as f:
                        celeb.image.save(image_filename, File(f), save=True)

                    self.stdout.write(self.style.SUCCESS(f"  ✓ Added {name}"))
                    success_count += 1
                    break  # Success, exit retry loop

                except Exception as e:
                    if attempt < max_retries - 1:
                        self.stdout.write(f"  ⚠ Attempt {attempt + 1} failed for {name}: {str(e)}")
                        self.stdout.write(f"  ⏳ Waiting {retry_delay} seconds before retry...")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                    else:
                        self.stdout.write(self.style.ERROR(f"  ✗ Failed {name} after {max_retries} attempts: {str(e)}"))
                        fail_count += 1
                        # Clean up failed download
                        if os.path.exists(image_path):
                            os.remove(image_path)

            # Add delay between celebrities to respect rate limits (except for last one)
            if i < len(CELEBRITIES) - 1:
                delay = 1  # 1 second between requests
                self.stdout.write(f"  ⏳ Rate limiting: waiting {delay} second(s)...")
                time.sleep(delay)

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(
            f"Seeding complete: {success_count} added, {skip_count} skipped, {fail_count} failed"
        ))
        self.stdout.write(f"Total celebrities in DB: {Celebrity.objects.count()}")

    def _seed_with_downloads(self, celeb_dir):
        """Seed celebrities by downloading from Wikimedia (may fail due to rate limits)"""
        success_count = 0
        skip_count = 0
        fail_count = 0

        for i, celeb_data in enumerate(CELEBRITIES):
            name = celeb_data['name']

            # Skip if already exists
            if Celebrity.objects.filter(name=name).exists():
                self.stdout.write(f"  ⏭ Skipping {name} (already exists)")
                skip_count += 1
                continue

            # Download image with retry logic
            safe_name = name.lower().replace(' ', '_').replace('.', '').replace("'", '')
            image_filename = f"{safe_name}.jpg"
            image_path = os.path.join(celeb_dir, image_filename)

            max_retries = 3
            retry_delay = 2  # seconds

            for attempt in range(max_retries):
                try:
                    self.stdout.write(f"  ⬇ Downloading {name}... (attempt {attempt + 1}/{max_retries})")
                    req = urllib.request.Request(
                        celeb_data['image_url'],
                        headers={
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                                          'Chrome/120.0.0.0 Safari/537.36',
                            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                            'Accept-Language': 'en-US,en;q=0.9',
                            'Accept-Encoding': 'gzip, deflate, br',
                            'DNT': '1',
                            'Connection': 'keep-alive',
                            'Upgrade-Insecure-Requests': '1',
                        }
                    )
                    with urllib.request.urlopen(req, timeout=30) as response:
                        with open(image_path, 'wb') as out_file:
                            out_file.write(response.read())

                    # Create celebrity record
                    celeb = Celebrity(
                        name=name,
                        category=celeb_data['category'],
                        description=celeb_data['description'],
                    )
                    with open(image_path, 'rb') as f:
                        celeb.image.save(image_filename, File(f), save=True)

                    self.stdout.write(self.style.SUCCESS(f"  ✓ Added {name}"))
                    success_count += 1
                    break  # Success, exit retry loop

                except Exception as e:
                    if attempt < max_retries - 1:
                        self.stdout.write(f"  ⚠ Attempt {attempt + 1} failed for {name}: {str(e)}")
                        self.stdout.write(f"  ⏳ Waiting {retry_delay} seconds before retry...")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                    else:
                        self.stdout.write(self.style.ERROR(f"  ✗ Failed {name} after {max_retries} attempts: {str(e)}"))
                        fail_count += 1
                        # Clean up failed download
                        if os.path.exists(image_path):
                            os.remove(image_path)

            # Add delay between celebrities to respect rate limits (except for last one)
            if i < len(CELEBRITIES) - 1:
                delay = 1  # 1 second between requests
                self.stdout.write(f"  ⏳ Rate limiting: waiting {delay} second(s)...")
                time.sleep(delay)

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(
            f"Seeding complete: {success_count} added, {skip_count} skipped, {fail_count} failed"
        ))
        self.stdout.write(f"Total celebrities in DB: {Celebrity.objects.count()}")

    def _seed_with_placeholders(self, celeb_dir):
        """Seed celebrities with placeholder images for testing"""
        from PIL import Image, ImageDraw, ImageFont
        import random

        success_count = 0
        skip_count = 0

        # Try to import PIL, if not available, inform user
        try:
            import PIL
        except ImportError:
            self.stdout.write(self.style.ERROR(
                "PIL (Pillow) is required for placeholder images. Install with: pip install Pillow"
            ))
            return

        for celeb_data in CELEBRITIES:
            name = celeb_data['name']

            # Skip if already exists
            if Celebrity.objects.filter(name=name).exists():
                self.stdout.write(f"  ⏭ Skipping {name} (already exists)")
                skip_count += 1
                continue

            # Create placeholder image
            safe_name = name.lower().replace(' ', '_').replace('.', '').replace("'", '')
            image_filename = f"{safe_name}.jpg"
            image_path = os.path.join(celeb_dir, image_filename)

            # Create a colored placeholder image
            colors = [(255, 100, 100), (100, 255, 100), (100, 100, 255), (255, 255, 100), (255, 100, 255), (100, 255, 255)]
            bg_color = random.choice(colors)

            img = Image.new('RGB', (250, 250), color=bg_color)
            draw = ImageDraw.Draw(img)

            # Try to add text (simplified, will work without font)
            try:
                # Use default font
                font = ImageFont.load_default()
                bbox = draw.textbbox((0, 0), name, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                x = (250 - text_width) // 2
                y = (250 - text_height) // 2
                draw.text((x, y), name, fill='white', font=font)
            except:
                # Fallback: just center text without font
                pass

            img.save(image_path)

            # Create celebrity record
            celeb = Celebrity(
                name=name,
                category=celeb_data['category'],
                description=celeb_data['description'],
            )
            with open(image_path, 'rb') as f:
                celeb.image.save(image_filename, File(f), save=True)

            self.stdout.write(self.style.SUCCESS(f"  ✓ Added {name} (placeholder)"))
            success_count += 1

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(
            f"Seeding complete: {success_count} added, {skip_count} skipped, 0 failed"
        ))
        self.stdout.write(f"Total celebrities in DB: {Celebrity.objects.count()}")

    def _seed_with_manual_images(self, celeb_dir):
        """Seed celebrities expecting images to be manually placed"""
        success_count = 0
        skip_count = 0
        fail_count = 0

        for celeb_data in CELEBRITIES:
            name = celeb_data['name']

            # Skip if already exists
            if Celebrity.objects.filter(name=name).exists():
                self.stdout.write(f"  ⏭ Skipping {name} (already exists)")
                skip_count += 1
                continue

            # Check for manually placed image
            safe_name = name.lower().replace(' ', '_').replace('.', '').replace("'", '')
            image_filename = f"{safe_name}.jpg"
            image_path = os.path.join(celeb_dir, image_filename)

            if os.path.exists(image_path):
                # Create celebrity record
                celeb = Celebrity(
                    name=name,
                    category=celeb_data['category'],
                    description=celeb_data['description'],
                )
                with open(image_path, 'rb') as f:
                    celeb.image.save(image_filename, File(f), save=True)

                self.stdout.write(self.style.SUCCESS(f"  ✓ Added {name}"))
                success_count += 1
            else:
                self.stdout.write(self.style.WARNING(f"  ⚠ Image not found for {name}: {image_path}"))
                fail_count += 1

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(
            f"Seeding complete: {success_count} added, {skip_count} skipped, {fail_count} failed"
        ))
        self.stdout.write(f"Total celebrities in DB: {Celebrity.objects.count()}")
        if fail_count > 0:
            self.stdout.write(self.style.WARNING(
                f"\nNote: {fail_count} images were not found. Place them manually in {celeb_dir}/"
            ))
