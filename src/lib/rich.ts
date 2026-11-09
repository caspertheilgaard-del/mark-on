/** Gør **ord** til <b>ord</b> i overskrifter. Resten escapes. */
export function rich(text: string): string {
  const esc = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
  return esc.replace(/\*\*(.+?)\*\*/g, '<b>$1</b>');
}
