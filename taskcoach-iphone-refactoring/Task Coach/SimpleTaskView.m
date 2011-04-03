//
//  SimpleTaskView.m
//  Task Coach
//
//  Created by Jérôme Laheurte on 27/03/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import "SimpleTaskView.h"
#import "Task_CoachAppDelegate.h"
#import "CDTask.h"

@implementation SimpleTaskView

- (id)initWithList:(CDList *)list
{
    if ((self = [super initWithNibName:@"SimpleTaskView" bundle:[NSBundle mainBundle]]))
    {
        NSFetchRequest *req = [[NSFetchRequest alloc] init];
        [req setEntity:[NSEntityDescription entityForName:@"CDTask" inManagedObjectContext:getManagedObjectContext()]];
        NSSortDescriptor *des = [[NSSortDescriptor alloc] initWithKey:@"name" ascending:YES];
        [req setSortDescriptors:[NSArray arrayWithObject:des]];
        [des release];
        if (list)
            [req setPredicate:[NSPredicate predicateWithFormat:@"list = %@", list]];
        resultsCtrl = [[NSFetchedResultsController alloc] initWithFetchRequest:req managedObjectContext:getManagedObjectContext() sectionNameKeyPath:nil cacheName:nil];
        [req release];
        NSError *error;
        if (![resultsCtrl performFetch:&error])
        {
            NSLog(@"Could not fetch tasks: %@", [error localizedDescription]);
        }
    }

    return self;
}

- (void)dealloc
{
    [resultsCtrl release];

    [super dealloc];
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)toInterfaceOrientation
{
    return YES;
}

#pragma mark - Table view data source

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView
{
    return [[resultsCtrl sections] count];
}

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section
{
    id <NSFetchedResultsSectionInfo> info = [[resultsCtrl sections] objectAtIndex:section];
    NSLog(@"%d objects.", [info numberOfObjects]);
    return [info numberOfObjects];
}

- (UITableViewCell *)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath
{
    static NSString *CellIdentifier = @"Cell";
    
    UITableViewCell *cell = [tableView dequeueReusableCellWithIdentifier:CellIdentifier];
    if (cell == nil)
    {
        cell = [[[UITableViewCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:CellIdentifier] autorelease];
    }
    
    CDTask *task = [resultsCtrl objectAtIndexPath:indexPath];
    cell.textLabel.text = task.name;
    
    return cell;
}

@end
