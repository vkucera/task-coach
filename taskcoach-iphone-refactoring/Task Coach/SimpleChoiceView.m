//
//  SimpleChoiceView.m
//  Task Coach
//
//  Created by Jérôme Laheurte on 17/03/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import "Task_CoachAppDelegate.h"
#import "SimpleChoiceView.h"


@implementation SimpleChoiceView

- (id)initWithEntityName:(NSString *)name completion:(void (^)(NSManagedObject *))completion
{
    if ((self = [super initWithNibName:@"SimpleChoiceView" bundle:[NSBundle mainBundle]]))
    {
        completionCb = completion;

        NSFetchRequest *req = [[NSFetchRequest alloc] init];
        [req setEntity:[NSEntityDescription entityForName:name inManagedObjectContext:getManagedObjectContext()]];
        NSSortDescriptor *des = [[NSSortDescriptor alloc] initWithKey:@"name" ascending:YES];
        [req setSortDescriptors:[NSArray arrayWithObject:des]];
        [des release];

        resultsCtrl = [[NSFetchedResultsController alloc] initWithFetchRequest:req managedObjectContext:getManagedObjectContext() sectionNameKeyPath:nil cacheName:nil];
        [req release];
    }

    return self;
}

- (void)dealloc
{
    [resultsCtrl release];

    [super dealloc];
}

#pragma mark - Table view data source

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView
{
    return [[resultsCtrl sections] count];
}

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section
{
    id <NSFetchedResultsSectionInfo> info = [[resultsCtrl sections] objectAtIndex:section];
    return [info numberOfObjects];
}

- (UITableViewCell *)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath
{
    static NSString *CellIdentifier = @"Cell";
    
    UITableViewCell *cell = [tableView dequeueReusableCellWithIdentifier:CellIdentifier];
    if (cell == nil) {
        cell = [[[UITableViewCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:CellIdentifier] autorelease];
    }

    cell.textLabel.text = [[resultsCtrl objectAtIndexPath:indexPath] name];
    
    return cell;
}

#pragma mark - Table view delegate

- (void)tableView:(UITableView *)tableView didSelectRowAtIndexPath:(NSIndexPath *)indexPath
{
    completionCb([resultsCtrl objectAtIndexPath:indexPath]);
}

@end
