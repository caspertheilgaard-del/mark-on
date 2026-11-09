import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

// Tekst med **fed** markering bruges i overskrifter (nøgleord i Bold 700).
const link = z.object({ label: z.string(), href: z.string() });

const placeholderOrImage = (image: () => z.ZodTypeAny) =>
  z.object({
    src: image().optional(),
    alt: z.string(),
    // Pladsholder vises synligt, til MarkOn har leveret billedet, fx "[BILLEDE: GAVESHOP]"
    placeholder: z.string().optional(),
  });

const sider = defineCollection({
  loader: glob({ pattern: '**/*.json', base: './src/content/sider' }),
  schema: ({ image }) =>
    z.object({
      seo: z.object({ title: z.string(), description: z.string() }),
      menu: z.string().describe('Hovedmenupunkt der markeres som aktivt'),
      breadcrumbs: z.array(z.object({ label: z.string(), href: z.string().optional() })),
      hero: z.object({
        heading: z.string(),
        body: z.array(z.string()),
        cta: link,
        image: placeholderOrImage(image),
      }),
      solutions: z.object({
        heading: z.string(),
        body: z.array(z.string()),
        cards: z.array(
          z.object({ heading: z.string(), body: z.array(z.string()), link: link.optional() }),
        ),
        images: z.array(placeholderOrImage(image)),
      }),
      process: z.object({
        heading: z.string(),
        body: z.array(z.string()),
        lead: z.string(),
        steps: z.array(z.object({ title: z.string(), text: z.string() })),
        after: z.array(z.string()),
        cta: link,
      }),
      faq: z.object({
        heading: z.string(),
        items: z.array(z.object({ question: z.string(), answer: z.array(z.string()) })),
        link: link.optional(),
      }),
      next: z.array(
        z.object({ title: z.string(), text: z.string(), href: z.string(), primary: z.boolean().default(false) }),
      ),
    }),
});

const site = defineCollection({
  loader: glob({ pattern: '**/*.json', base: './src/content/site' }),
  schema: ({ image }) =>
    z.object({
      logo: image(),
      tagline: z.string(),
      phone: z.object({ label: z.string(), href: z.string() }),
      email: z.string(),
      menu: z.array(link),
      cta: link,
      locations: z.array(
        z.object({ name: z.string(), lines: z.array(z.string()), phone: z.string().optional(), email: z.string().optional() }),
      ),
      legal: z.array(z.object({ label: z.string(), href: z.string().optional() })),
    }),
});

export const collections = { sider, site };
