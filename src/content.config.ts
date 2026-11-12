import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

/*
 * Hver side er en JSON-fil i src/content/sider/ med en liste af sektioner ("blocks").
 * Hver sektionstype har sin egen komponent i src/components/blocks/.
 * Overskrifter kan markere nøgleord med **fed** (vises i Bold 700).
 * Pladsholdere som [ANTAL] og [BILLEDE: ...] bevares synligt, til MarkOn udfylder dem.
 */

const link = z.object({ label: z.string(), href: z.string() });

const sider = defineCollection({
  loader: glob({ pattern: '**/*.json', base: './src/content/sider' }),
  schema: ({ image }) => {
    // Et billede, eller en synlig pladsholder til MarkOn har leveret billedet.
    const media = z.object({
      src: image().optional(),
      alt: z.string(),
      placeholder: z.string().optional(),
      background: z.enum(['sand', 'white']).default('sand'),
      position: z.string().optional(),
    });

    const hero = z.object({
      type: z.literal('hero'),
      variant: z.enum(['standard', 'large', 'front']).default('standard'),
      eyebrow: z.string().optional(),
      heading: z.string(),
      body: z.array(z.string()).default([]),
      ctas: z.array(link).default([]),
      stats: z.array(z.object({ value: z.string(), label: z.string() })).optional(),
      media: z
        .discriminatedUnion('kind', [
          z.object({ kind: z.literal('image'), image: media }),
          z.object({
            kind: z.literal('swap'),
            alt: z.string(),
            background: z.string(),
            interval: z.number().default(2).describe('Sekunder pr. billede'),
            images: z.array(image()),
          }),
          z.object({ kind: z.literal('collage'), images: z.array(media).length(3) }),
          z.object({
            kind: z.literal('pair'),
            align: z.enum(['start', 'end']).default('start'),
            maxWidth: z.number().optional(),
            items: z.array(
              z.object({
                image: media,
                shape: z.enum(['portrait', 'tall', 'circle']),
                grow: z.number().default(1),
                offsetTop: z.number().default(0),
                offsetBottom: z.number().default(0),
                dot: z.boolean().default(false),
                shadow: z.boolean().default(false),
              }),
            ),
          }),
        ])
        .optional(),
    });

    const cards = z.object({
      type: z.literal('cards'),
      heading: z.string(),
      body: z.array(z.string()).default([]),
      cards: z.array(z.object({ heading: z.string(), body: z.array(z.string()), link: link.optional() })).default([]),
      gallery: z.array(media).default([]),
    });

    const tiles = z.object({
      type: z.literal('tiles'),
      heading: z.string(),
      body: z.array(z.string()).default([]),
      tiles: z.array(
        z.object({
          title: z.string(),
          text: z.string().optional(),
          href: z.string().optional(),
          linkLabel: z.string().optional(),
          image: media.optional(),
          swap: z.object({ alt: z.string(), images: z.array(image()) }).optional(),
        }),
      ),
    });

    const band = z.object({
      type: z.literal('band'),
      variant: z.enum(['standard', 'large']).default('standard'),
      heading: z.string(),
      body: z.array(z.string()).default([]),
      lead: z.string().optional(),
      steps: z.array(z.object({ kicker: z.string().optional(), title: z.string(), text: z.string() })).optional(),
      after: z.array(z.string()).default([]),
      links: z.array(link).default([]),
      cta: link.optional(),
      link: link.optional(),
    });

    const categories = z.object({
      type: z.literal('categories'),
      heading: z.string(),
      text: z.string(),
      items: z.array(
        z.object({
          title: z.string(),
          href: z.string(),
          text: z.string(),
          links: z.array(link),
          more: z.string(),
          image: media,
          ratio: z.enum(['portrait', 'tall']),
          offset: z.number().default(0),
          pill: z.enum(['top', 'bottom']).default('bottom'),
        }),
      ),
      audiences: z.array(z.object({ kicker: z.string(), title: z.string(), href: z.string() })).default([]),
    });

    const logos = z.object({ type: z.literal('logos'), label: z.string(), names: z.array(z.string()) });

    const cases = z.object({
      type: z.literal('cases'),
      heading: z.string(),
      link: link,
      items: z.array(
        z.object({ title: z.string(), text: z.string(), href: z.string(), image: media, size: z.enum(['large', 'small', 'wide']) }),
      ),
    });

    const quote = z.object({ type: z.literal('quote'), text: z.string(), author: z.string() });

    const caseBlock = z.object({
      type: z.literal('case'),
      variant: z.enum(['strip', 'banner']).default('strip'),
      kicker: z.string(),
      title: z.string(),
      href: z.string(),
      linkLabel: z.string(),
      image: media,
    });

    const features = z.object({
      type: z.literal('features'),
      heading: z.string(),
      text: z.string(),
      items: z.array(z.object({ image: media, title: z.string(), text: z.string(), label: z.string(), value: z.string() })),
    });

    const products = z.object({
      type: z.literal('products'),
      heading: z.string(),
      text: z.string(),
      items: z.array(z.object({ image: media, title: z.string(), text: z.string(), meta: z.string() })),
    });

    const split = z.object({
      type: z.literal('split'),
      heading: z.string(),
      text: z.string(),
      cards: z.array(z.object({ title: z.string(), text: z.string() })),
    });

    const values = z.object({
      type: z.literal('values'),
      heading: z.string(),
      text: z.string(),
      storyHeading: z.string(),
      story: z.string(),
      processHeading: z.string(),
      steps: z.array(z.object({ title: z.string(), text: z.string() })),
    });

    const team = z.object({
      type: z.literal('team'),
      heading: z.string(),
      text: z.string(),
      members: z.array(z.object({ photo: media, name: z.string(), role: z.string(), link: link })),
    });

    const info = z.object({
      type: z.literal('info'),
      cards: z.array(
        z.object({
          heading: z.string(),
          text: z.string(),
          extra: z.string().optional(),
          cta: link.optional(),
          links: z.array(link).default([]),
        }),
      ),
    });

    const quoteForm = z.object({
      type: z.literal('quoteForm'),
      heading: z.string(),
      body: z.string(),
      channels: z.array(z.object({ icon: z.enum(['phone', 'mail']), label: z.string(), value: z.string(), href: z.string() })).default([]),
      needs: z.array(z.object({ label: z.string(), checked: z.boolean().default(false) })),
      note: z.string().optional(),
    });

    const locations = z.object({
      type: z.literal('locations'),
      items: z.array(z.object({ name: z.string(), lines: z.array(z.string()), email: z.string().optional() })),
      card: z.object({ kicker: z.string(), title: z.string(), href: z.string() }),
    });

    const product = z.object({
      type: z.literal('product'),
      heading: z.string(),
      body: z.string(),
      gallery: z.array(media.extend({ shape: z.enum(['square', 'circle']).default('square') })),
      facts: z.array(z.object({ label: z.string(), value: z.string() })),
      formHeading: z.string(),
    });

    const faq = z.object({
      type: z.literal('faq'),
      variant: z.enum(['standard', 'split']).default('standard'),
      heading: z.string(),
      intro: z.string().optional(),
      cta: link.optional(),
      link: link.optional(),
      spaceAbove: z.number().optional().describe('Luft over sektionen i px, hvis den afviger'),
      items: z.array(z.object({ question: z.string(), answer: z.array(z.string()) })),
    });

    const next = z.object({
      type: z.literal('next'),
      variant: z.enum(['standard', 'large']).default('standard'),
      kicker: z.string().default('Hvor vil du hen nu?'),
      items: z.array(z.object({ title: z.string(), text: z.string(), href: z.string(), primary: z.boolean().default(false) })),
    });

    return z.object({
      url: z.string().describe('Sidens adresse, fx /firmajulegaver/'),
      seo: z.object({ title: z.string(), description: z.string() }),
      menu: z.string().optional().describe('Hovedmenupunkt der markeres som aktivt'),
      scale: z.enum(['standard', 'large']).default('standard').describe('Typografi: standard (44 px h2) eller large (48 px h2)'),
      breadcrumbs: z.array(z.object({ label: z.string(), href: z.string().optional() })).optional(),
      blocks: z.array(
        z.discriminatedUnion('type', [
          hero, cards, tiles, band, categories, logos, cases, quote, caseBlock, features, products,
          split, values, team, info, quoteForm, locations, product, faq, next,
        ]),
      ),
    });
  },
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
