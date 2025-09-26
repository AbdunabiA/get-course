import { ReactNode } from 'react'

const ContainerWrapper = ({ children }: { children: ReactNode }) => {
  return <div className='mx-auto max-w-[1440px] container px-4'>{children}</div>
}

export default ContainerWrapper