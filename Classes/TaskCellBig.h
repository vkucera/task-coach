//
//  TaskCellBig.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 22/02/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import <Foundation/Foundation.h>

#import "TaskCell.h"

@interface TaskCellBig : TaskCell
{
	UILabel *infosLabel;
	UILabel *categoriesLabel;
	NSMutableArray *categories;
}

@property (nonatomic, retain) IBOutlet UILabel *infosLabel;
@property (nonatomic, retain) IBOutlet UILabel *categoriesLabel;

@end
