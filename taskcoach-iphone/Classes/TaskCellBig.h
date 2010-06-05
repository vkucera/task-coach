//
//  TaskCellBig.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 22/02/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import <Foundation/Foundation.h>

#import "TaskCell.h"

@interface TaskCellBig : TaskCell
{
	UILabel *infosLabel;
	UILabel *categoriesLabel;
}

@property (nonatomic, retain) IBOutlet UILabel *infosLabel;
@property (nonatomic, retain) IBOutlet UILabel *categoriesLabel;

@end
