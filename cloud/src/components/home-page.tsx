// import { useDeleteOrganization } from "@/src/api/organizations";
// import { DeleteButton } from "@/src/components/delete-button";
// import { Button } from "@/src/components/ui/button";
// import { useAuth } from "@/src/contexts/auth";
// import { useOrganization } from "@/src/contexts/organization";

export function HomePage() {
  // const { user, logout } = useAuth();
  // const { currentOrganization } = useOrganization();
  // const deleteOrganizationMutation = useDeleteOrganization();

  // const handleDeleteOrganization = async () => {
  //   if (!currentOrganization) return;
  //   await deleteOrganizationMutation.mutateAsync(currentOrganization.id);
  // };

  // return (
  //   <div className="w-screen h-screen flex flex-col">
  //     <div className="flex justify-end items-center gap-x-2 p-4">
  //       {currentOrganization && (
  //         <>
  //           <div className="text-sm text-muted-foreground">
  //             {currentOrganization.name}
  //           </div>
  //           <DeleteButton
  //             size="sm"
  //             onDelete={handleDeleteOrganization}
  //             title={`Delete organization ${currentOrganization.name}`}
  //             confirmationText={currentOrganization.name}
  //           >
  //             Delete
  //           </DeleteButton>
  //         </>
  //       )}
  //     </div>
  //     <div className="flex-1 flex flex-col gap-y-4 justify-center items-center font-handwriting">
  //       <div className="text-2xl">
  //         {user!.name ? `Welcome, ${user!.name?.split(' ')[0]}!` : 'Welcome!'}
  //       </div>
  //       <Button variant="secondary" onClick={logout}>
  //         Logout
  //       </Button>
  //     </div>
  //   </div>
  // );
  return <div>Hello, World!</div>;
}
