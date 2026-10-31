import { Suspense } from "react";
import { Admissions } from "@/features/admissions";
import { Loading } from "@/components/ui";
export default function AdmissionsPage() { return <Suspense fallback={<Loading />}><Admissions /></Suspense>; }
